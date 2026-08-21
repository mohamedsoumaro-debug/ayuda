# Vídeo del producto ganador

`salida/anuncio.mp4` — vertical 1080x1920, 25 s, con subtítulos incrustados y pista de
audio en silencio (para que TikTok/Meta lo acepten; la música la pones tú al subirlo).

## Cambiar los textos

Edita `config.json` y vuelve a generar:

```bash
cd video
python3 render.py
```

Tarda unos 45 segundos. El resultado se sobrescribe en `salida/anuncio.mp4`.

| Campo | Qué es |
|---|---|
| `producto` | Nombre que sale en la tarjeta y en el cierre |
| `gancho` | Los 3 primeros segundos. Lo más importante del vídeo |
| `problema` | El dolor, en 3-5 palabras |
| `solucion` | La frase que resuelve el problema |
| `beneficios` | Tres motivos de compra, cortos |
| `precio`, `envio`, `tienda`, `cta` | La pantalla final |
| `color_acento` | El color de marca (hex) |

## Añadir tus fotos

Mete 2 o 3 imágenes en `video/fotos/` (jpg o png) y vuelve a lanzar `render.py`.
El vídeo las usa de fondo con zoom lento en lugar de los fondos de color.
Orden alfabético: la primera se usa en el plano del producto, la segunda en los
beneficios, la última en el gancho.

## Estructura (25 s)

| Seg | Escena |
|---|---|
| 0-3 | Gancho |
| 3-7 | Producto |
| 7-14 | Tres beneficios |
| 14-19 | Antes / Después |
| 19-25 | Precio y llamada a la acción |

Para anuncio pagado, recorta a los primeros 15 s.

## Requisitos

```bash
pip install pillow imageio-ffmpeg
```
