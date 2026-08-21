# Hacer el vídeo con ChatGPT — copiar y pegar

## Paso 1 · Pega esto en ChatGPT

Rellena las 5 líneas de arriba y envíalo tal cual.

```
Producto: [nombre de tu producto]
Qué problema resuelve: [en una frase]
A quién va dirigido: [tipo de cliente]
Precio: [precio]
Mi tienda: [nombre o web]

Actúa como guionista de anuncios UGC para TikTok y Reels.

Quiero un vídeo vertical de 25 segundos para vender ese producto.

Dame dos cosas:

1) Una tabla con el guion segundo a segundo: columna de segundos,
   qué se ve en pantalla, el texto que aparece escrito, y la voz en off.
   Estructura: gancho (0-3s), producto (3-7s), demostración (7-14s),
   antes/después (14-19s), precio y llamada a la acción (19-25s).
   Español de España, tono natural de persona real, nada de lenguaje
   publicitario. El gancho tiene que doler en los 3 primeros segundos.

2) Cinco prompts para Sora, uno por plano, listos para copiar.
   Cada prompt: formato vertical 9:16, duración del plano, estilo grabado
   con móvil con luz natural, y sin texto dentro del vídeo.

Al final dame 5 ganchos alternativos para ir probando cuál funciona mejor.
```

## Paso 2 · Genera los planos con Sora

En la app de ChatGPT, abre **Sora** (o entra en sora.com con tu misma cuenta).
Pega los 5 prompts **de uno en uno** y descarga cada clip.

Si un plano sale raro, cambia **una sola cosa** del prompt (la luz, el ángulo o
el entorno) y regenéralo. Cambiarlo todo a la vez te deja sin control.

## Paso 3 · Los planos del producto, con tus fotos

Sora **no va a clonar tu producto real**: inventa uno parecido. Úsalo para el
ambiente (manos, cocina, escritorio, calle) y en los planos donde se ve el
producto mete **tus fotos reales**. Ese mix es el que convierte.

## Paso 4 · Montarlo

CapCut (gratis, móvil u ordenador):

1. Proyecto vertical 9:16.
2. Ordena los clips según la tabla del paso 1.
3. Pega los textos de la columna "texto en pantalla".
4. Subtítulos automáticos siempre activados.
5. Música: una en tendencia del propio TikTok, sube más el alcance que una de stock.
6. Exporta a 1080x1920, 30 fps.

## Si prefieres saltarte todo esto

Ya tienes el vídeo montado en `salida/anuncio.mp4`. Cambia los textos en
`config.json`, ejecuta `python3 render.py` y lo tienes en 45 segundos.
