# Cámara: interacción con las manos

Proyecto experimental de visión por computador para crear experiencias interactivas con gestos capturados por webcam.

## Esta rama: `basic-impl`

Implementación básica sobre la que se construyen las demás experiencias. Detecta las manos con MediaPipe, dibuja marcadores y ofrece gestos simples para servir de ejemplo y base reutilizable.

En su configuración actual, la mano objetivo muestra puntos de color y puede activar líneas temporales o persistentes al acercar determinados puntos. La otra mano muestra puntos blancos únicamente en los dedos que están levantados.

## Ejecutar

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

En la primera ejecución se descarga el modelo de [MediaPipe Hand Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python) en `models/`. Concede permiso de cámara si se solicita y pulsa `Q` para cerrar.

## Arquitectura

| Componente | Responsabilidad |
| --- | --- |
| `main.py` | Define qué marcadores y gestos están activos en cada fotograma. |
| `camara/config.py` | Centraliza mano objetivo, colores, puntos de MediaPipe y umbrales. |
| `camara/tracker.py` | Convierte cada fotograma en manos detectadas y sus 21 puntos normalizados. |
| `camara/detectors.py` | Dibuja puntos, estima dedos levantados y detecta contactos. |
| `camara/actions.py` | Contiene las acciones disparadas por los gestos, como dibujar líneas. |
| `camara/app.py` | Gestiona webcam, bucle de fotogramas, lienzo persistente y ventana. |

El flujo es: webcam → `HandTracker` → `process_frame` en `main.py` → detectores y acciones → ventana de OpenCV.

## Cómo funciona

`main.py` recibe las manos detectadas en cada fotograma. `put_dot(...)` dibuja un marcador en un punto de MediaPipe; `put_dot_if_raised(...)` lo hace solo si el dedo está extendido. `on_touch(...)` compara la distancia entre dos puntos con el tamaño de la palma y dispara una acción mientras el contacto continúa.

La acción `write_straight_line(...)` une, de pulgar a meñique, las puntas levantadas de la mano blanca. El lienzo persistente se conserva durante la ejecución y se limpia al cerrar el programa.

Para crear una experiencia nueva, parte de esta rama, ajusta los valores de `camara/config.py` y decide en `main.py` qué detectores y acciones usar. La detección de dedos es una estimación 2D: puede variar si la mano gira mucho o una articulación queda oculta.

## Otras ramas

- `master`: índice y descripción general del proyecto.
- `drum-progression`: creador de patrones de batería controlado con gestos.
