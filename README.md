# Marcadores sobre la mano

Abre la webcam y dibuja los marcadores de `main.py`. En la mano del bloque blanco, cada punta lleva un punto blanco solo cuando el dedo está extendido. Si los puntos rojo (4) y verde (8) de la otra mano se acercan, aparecen líneas blancas temporales entre los dedos blancos levantados. Si se tocan los puntos 4 y 14, las mismas líneas quedan dibujadas hasta cerrar el programa.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

La primera ejecución descarga el modelo de [MediaPipe Hand Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python) en `models/`. Permite el acceso a la cámara si el sistema lo solicita. Pulsa **Q** para cerrar. Tras editar el código, cierra y vuelve a ejecutar el programa.

## Cómo está organizado

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | Llamadas explícitas a `put_dot` y `on_touch`. Aquí decides qué ocurre. |
| `camara/config.py` | Valores editables: mano, colores, puntos y sensibilidad. |
| `camara/tracker.py` | MediaPipe: recibe un fotograma y devuelve manos con puntos `(x, y)` normalizados. |
| `camara/detectors.py` | Implementa `put_dot`, `put_dot_if_raised` y `on_touch`. |
| `camara/actions.py` | Funciones que se ejecutan al detectar un gesto. |
| `camara/app.py` | Bucle de cámara y lienzo permanente; llama a `process_frame` en cada imagen. |

Para añadir otro marcador, define el punto y el color en `camara/config.py` y añade otra llamada `put_dot(...)` en `main.py`. Para otro gesto, define una pareja de puntos, crea su función en `camara/actions.py` y añade `on_touch(frame, hand, pareja, accion)` en `main.py`.

`put_dot_if_raised(...)` usa las dos articulaciones de cada dedo para estimar si está extendido. Puedes ajustar `EXTENDED_ANGLE_DEGREES` en `camara/config.py`. Es una estimación en 2D: si la mano gira mucho o una articulación queda tapada, la detección puede fallar.

`write_straight_line` en `camara/actions.py` une, de pulgar a meñique, las puntas que estén extendidas en la mano `WHITE_HAND`. Cambia `LINE_THICKNESS` en `camara/config.py` para ajustar el grosor.

El lienzo permanente se guarda en memoria durante la ejecución y se superpone a cada fotograma. Se vacía al cerrar y volver a abrir el programa.

`TOUCH_THRESHOLD` es una fracción de la longitud de la palma, no una distancia fija en píxeles. `on_touch` ejecuta la acción en cada fotograma mientras dura el contacto. La detección es una aproximación en 2D: dos puntos pueden parecer juntos en la imagen aunque estén separados en profundidad.

## CÓMO CREAR
Existe una rama `basic-imp` con un proyecto muy básico para detectar dedos y gestos simples, donde es fácil ver la arquitectura. Puedes crear una rama a partir de ella para editarla y configurar tus propios gestos.