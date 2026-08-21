#!/usr/bin/env python3
"""Genera un video vertical 9:16 para anuncio de producto.

Uso:  python3 render.py [config.json] [salida.mp4]

Si hay imagenes en video/fotos/ las usa como fondo (efecto zoom lento).
Si no, usa fondos de color animados.
"""
import json
import os
import subprocess
import sys
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_font_cache = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    return _font_cache[key]


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return 3 * t * t - 2 * t * t * t


def wrap(draw, text, fnt, max_w):
    """Parte el texto en lineas que caben en max_w."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        probe = (cur + " " + w).strip()
        if draw.textlength(probe, font=fnt) <= max_w or not cur:
            cur = probe
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, text, fnt, max_w, cx, top, fill, line_gap=1.18, align="center",
               shadow=True, max_words=None):
    """Dibuja texto multilinea centrado. Devuelve la altura ocupada."""
    if max_words is not None:
        text = " ".join(text.split()[:max_words])
    lines = wrap(draw, text, fnt, max_w)
    lh = int(fnt.size * line_gap)
    y = top
    for ln in lines:
        tw = draw.textlength(ln, font=fnt)
        x = cx - tw / 2 if align == "center" else cx
        if shadow:
            draw.text((x + 4, y + 5), ln, font=fnt, fill=(0, 0, 0, 140))
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y - top


def rounded(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)


# ---------------------------------------------------------------- fondos
def gradient_bg(base, accent, t, warm=False):
    """Fondo con degradado suave que respira con el tiempo."""
    small = Image.new("RGB", (36, 64), base)
    d = ImageDraw.Draw(small)
    pulse = 0.5 + 0.5 * math.sin(t * 0.7)
    for y in range(64):
        k = (y / 63) ** 1.4
        mix = k * (0.30 + 0.16 * pulse)
        if warm:
            mix *= 1.5
        col = tuple(int(base[i] + (accent[i] - base[i]) * mix) for i in range(3))
        d.line([(0, y), (36, y)], fill=col)
    return small.resize((W, H), Image.BICUBIC)


def photo_bg(img, t, dur, darken=0.55):
    """Ken Burns: zoom lento sobre una foto, recortada a 9:16."""
    zoom = 1.06 + 0.10 * (t / dur)
    tw, th = int(W * zoom), int(H * zoom)
    src = img.copy()
    sw, sh = src.size
    scale = max(tw / sw, th / sh)
    src = src.resize((int(sw * scale) + 1, int(sh * scale) + 1), Image.BICUBIC)
    sw, sh = src.size
    drift = int((sh - th) * 0.5 * (0.4 + 0.6 * (t / dur)))
    src = src.crop(((sw - tw) // 2, drift, (sw - tw) // 2 + tw, drift + th))
    src = src.resize((W, H), Image.BICUBIC)
    veil = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.blend(src, veil, darken)


# ---------------------------------------------------------------- escenas
def sc_gancho(im, d, t, dur, C, photos):
    """0-3 s: el gancho. Palabra a palabra, agresivo."""
    words = C["gancho"].split()
    shown = min(len(words), int(t / (dur * 0.62) * len(words)) + 1)
    fnt = font(104)
    txt = " ".join(words[:shown])
    lines = wrap(d, txt, fnt, W - 150)
    total = len(lines) * int(fnt.size * 1.14)
    top = H * 0.36 - total / 2
    # barra de acento que crece
    bw = int((W - 150) * ease_out(t / 0.6))
    d.rectangle([75, top - 60, 75 + bw, top - 46], fill=C["ACC"])
    text_block(d, txt, fnt, W - 150, W / 2, top, C["TXT"])
    if t > dur * 0.55:
        sub = font(48, bold=False)
        a = ease_out((t - dur * 0.55) / 0.5)
        y = H * 0.36 + total / 2 + 70 + int(40 * (1 - a))
        text_block(d, C["problema"].upper(), sub, W - 200, W / 2, y,
                   tuple(list(C["ACC"])))


def sc_solucion(im, d, t, dur, C, photos):
    """3-7 s: aparece el producto."""
    a = ease_out(t / 0.8)
    fnt = font(92)
    y = H * 0.30 + int(70 * (1 - a))
    text_block(d, C["solucion"], fnt, W - 160, W / 2, y, C["TXT"])
    # tarjeta con el nombre del producto
    if t > 0.7:
        b = ease_out((t - 0.7) / 0.7)
        fn2 = font(76)
        name = C["producto"].upper()
        tw = min(d.textlength(name, font=fn2), W - 220)
        pad = 46
        bw, bh = tw + pad * 2, fn2.size + pad * 1.4
        cy = H * 0.56 + int(50 * (1 - b))
        box = [W / 2 - bw / 2, cy, W / 2 + bw / 2, cy + bh]
        rounded(d, box, 28, C["ACC"])
        d.text((W / 2 - tw / 2, cy + pad * 0.55), name, font=fn2, fill=(255, 255, 255))


def sc_beneficios(im, d, t, dur, C, photos):
    """7-14 s: los tres motivos de compra, uno a uno."""
    fnt = font(66)
    tag = font(40, bold=False)
    text_block(d, "POR QUÉ FUNCIONA", tag, W - 200, W / 2, H * 0.20, C["ACC"])
    step = dur / (len(C["beneficios"]) + 0.6)
    y = H * 0.31
    for i, ben in enumerate(C["beneficios"]):
        start = i * step
        if t < start:
            break
        a = ease_out((t - start) / 0.55)
        lines = wrap(d, ben, fnt, W - 300)
        bh = len(lines) * int(fnt.size * 1.16) + 74
        x_off = int(90 * (1 - a))
        box = [90 + x_off, y, W - 90 + x_off, y + bh]
        rounded(d, box, 26, (255, 255, 255, 255) if False else (26, 26, 32))
        d.ellipse([124 + x_off, y + bh / 2 - 17, 158 + x_off, y + bh / 2 + 17],
                  fill=C["ACC"])
        ty = y + 37
        for ln in lines:
            d.text((186 + x_off, ty), ln, font=fnt, fill=C["TXT"])
            ty += int(fnt.size * 1.16)
        y += bh + 34


def sc_prueba(im, d, t, dur, C, photos):
    """14-19 s: antes / después."""
    a = ease_in_out(min(1.0, t / 1.0))
    mid = H * 0.5
    # panel superior (antes) apagado, inferior (después) con acento
    d.rectangle([0, 0, W, mid], fill=(22, 22, 26))
    grad = Image.new("RGB", (W, int(H - mid)), C["ACC"])
    im.paste(grad, (0, int(mid)))
    d.rectangle([0, mid - 5, W, mid + 5], fill=(13, 13, 16))

    lbl = font(44, bold=False)
    big = font(88)
    # cada mitad con su texto centrado en vertical
    n1 = len(wrap(d, C["problema"], big, W - 160))
    top1 = mid * 0.5 - n1 * big.size * 1.18 / 2
    d.text((80, top1 - 90), C["antes"].upper(), font=lbl, fill=(150, 150, 158))
    text_block(d, C["problema"], big, W - 160, W / 2, top1, (120, 120, 128))

    n2 = len(wrap(d, C["solucion"], big, W - 160))
    top2 = mid + (H - mid) * 0.5 - n2 * big.size * 1.18 / 2
    d.text((80, top2 - 90), C["despues"].upper(), font=lbl, fill=(255, 255, 255))
    if a > 0.15:
        text_block(d, C["solucion"], big, W - 160, W / 2,
                   top2 + int(30 * (1 - a)), (255, 255, 255))


def sc_cierre(im, d, t, dur, C, photos):
    """19-25 s: precio, tienda, llamada a la accion."""
    a = ease_out(t / 0.7)
    fnt = font(120)
    y = H * 0.30 + int(60 * (1 - a))
    text_block(d, C["producto"].upper(), fnt, W - 140, W / 2, y, C["TXT"])

    if t > 0.5:
        b = ease_out((t - 0.5) / 0.6)
        fp = font(150)
        pw = d.textlength(C["precio"], font=fp)
        py = H * 0.50 + int(40 * (1 - b))
        d.text((W / 2 - pw / 2, py), C["precio"], font=fp, fill=C["ACC"])

    if t > 1.1:
        c = ease_out((t - 1.1) / 0.6)
        fe = font(46, bold=False)
        text_block(d, C["envio"], fe, W - 200, W / 2,
                   H * 0.66 + int(30 * (1 - c)), (200, 200, 208))

    if t > 1.7:
        e = ease_out((t - 1.7) / 0.6)
        fb = font(64)
        label = C["tienda"]
        tw = d.textlength(label, font=fb)
        pad = 48
        bw, bh = tw + pad * 2, fb.size + pad * 1.3
        cy = H * 0.75 + int(40 * (1 - e))
        # el boton late suavemente para pedir el clic
        pulse = 1 + 0.02 * math.sin((t - 1.7) * 6)
        bw, bh = bw * pulse, bh * pulse
        rounded(d, [W / 2 - bw / 2, cy, W / 2 + bw / 2, cy + bh], 999, C["ACC"])
        d.text((W / 2 - tw / 2, cy + pad * 0.5), label, font=fb, fill=(255, 255, 255))
        fc = font(42, bold=False)
        text_block(d, C["cta"], fc, W - 200, W / 2, cy + bh + 36, (170, 170, 180))


SCENES = [
    (sc_gancho, 3.0, "hook"),
    (sc_solucion, 4.0, "producto"),
    (sc_beneficios, 7.0, "beneficios"),
    (sc_prueba, 5.0, "antes/despues"),
    (sc_cierre, 6.0, "cierre"),
]


def load_photos():
    d = os.path.join(BASE, "fotos")
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        if name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            try:
                out.append(Image.open(os.path.join(d, name)).convert("RGB"))
            except Exception:
                pass
    return out


def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "config.json")
    out_path = (sys.argv[2] if len(sys.argv) > 2
                else os.path.join(BASE, "salida", "anuncio.mp4"))
    with open(cfg_path) as f:
        C = json.load(f)
    C["BG"] = hex_rgb(C["color_fondo"])
    C["ACC"] = hex_rgb(C["color_acento"])
    C["TXT"] = hex_rgb(C["color_texto"])

    photos = load_photos()
    total = sum(s[1] for s in SCENES)
    n_frames = int(total * FPS)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ff, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-",
        # pista de silencio: sin audio algunas plataformas rechazan el archivo
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "128k",
        out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for i in range(n_frames):
        t_glob = i / FPS
        # localizar escena
        acc = 0.0
        fn, dur, _ = SCENES[-1]
        t_loc = t_glob
        for f_, d_, _n in SCENES:
            if t_glob < acc + d_:
                fn, dur, t_loc = f_, d_, t_glob - acc
                break
            acc += d_

        is_cierre = fn is sc_cierre
        if photos and fn in (sc_solucion, sc_beneficios):
            idx = 0 if fn is sc_solucion else min(1, len(photos) - 1)
            im = photo_bg(photos[idx], t_loc, dur)
        elif photos and fn is sc_gancho:
            im = photo_bg(photos[-1], t_loc, dur, darken=0.68)
        else:
            im = gradient_bg(C["BG"], C["ACC"], t_glob, warm=is_cierre)
        im = im.convert("RGB")
        d = ImageDraw.Draw(im, "RGBA")

        fn(im, d, t_loc, dur, C, photos)

        # fundido de entrada y de salida
        if t_glob < 0.35 or t_glob > total - 0.35:
            k = (t_glob / 0.35) if t_glob < 0.35 else ((total - t_glob) / 0.35)
            im = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), im,
                             max(0.0, min(1.0, k)))
            d = ImageDraw.Draw(im, "RGBA")

        # barra de progreso: sube la retencion, el ojo sabe cuanto queda
        d.rectangle([0, H - 12, W * (t_glob / total), H], fill=C["ACC"])

        proc.stdin.write(im.tobytes())

    proc.stdin.close()
    proc.wait()
    size = os.path.getsize(out_path) / 1e6
    print(f"OK  {out_path}  {total:.0f}s  {n_frames} frames  {size:.1f} MB")


if __name__ == "__main__":
    main()
