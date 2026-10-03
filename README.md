# Cámara: interacción con las manos

Proyecto experimental de visión por computador para crear experiencias interactivas con gestos capturados por webcam.

## Esta rama: `drum-progression`

Esta rama crea patrones de batería que se reproducen en un compás de cuatro tiempos en bucle. El tempo inicial es **80 BPM** y se puede ajustar con la mano.

## Cómo funciona

La mano izquierda escribe los tiempos: **meñique, anular, medio e índice** equivalen a los tiempos 1–4. Dedo levantado = sonido (`1`); dedo retraído = silencio (`0`). Su pulgar activa el control de tempo.

La mano derecha elige el instrumento: índice = **kick**, medio = **snare**, anular = **hihat** y meñique = **splash**. Las cuatro puntas tienen un punto de color para confirmar el sonido con el pulgar derecho (círculo verde). El punto de la **base del meñique** cambia entre modo negras (negro) y modo corcheas (morado). Arriba, en el centro, aparece siempre `modo: negras` o `modo: corcheas`. Separa los dedos antes de volver a confirmar o cambiar de modo.

En modo negras, confirmar un sonido escribe sus cuatro tiempos y devuelve esa fila a cuatro notas. En modo corcheas, la primera confirmación escribe las cuatro primeras notas de ese sonido; la segunda escribe las cuatro últimas; las siguientes alternan entre ambas mitades. Cambiar de modo no altera los patrones guardados hasta que confirmes un sonido.

La mano de los puntos blancos tiene otro punto en la **base del meñique**. Manténlo pulsado con el pulgar de esa misma mano para controlar el tempo: al soltarlo, el BPM se queda donde esté. Su umbral de contacto es un poco mayor que el de los sonidos. El punto y el número de BPM se vuelven morados mientras lo mantienes pulsado. Cada vez que lo pulsas se calibra la orientación actual: con la mano plana frente a la cámara, gírala **a la izquierda para bajar** el tempo o **a la derecha para subirlo**, sin acercarla ni alejarla. El tempo se limita a 40–180 BPM. La sensibilidad se ajusta con `SLIDER_BPM_PER_DEGREE` en `camara/config.py`; cambia su signo si el giro responde al revés en tu cámara.

Las cuatro filas están siempre arriba a la izquierda, empezando en `0 0 0 0`. Solo el instrumento elegido pasa a ocho notas al confirmar corcheas; los demás conservan sus cuatro negras. El panel usa ocho columnas fijas (`1 & 2 & 3 & 4 &`), de modo que los números quedan alineados y las negras ocupan una columna sí y otra no. Arriba a la derecha se muestra el BPM actual.

### Modo acordes

El punto de la **base del anular derecho** alterna entre beat y acordes al tocarlo con el **pulgar derecho**. El modo aparece debajo del rótulo de negras/corcheas y la tonalidad debajo de él. La tonalidad inicial es **C mayor**.

En acordes se ocultan los controles de batería y tempo. Quedan visibles el toggle beat/acordes y el de la **punta del medio derecho**, que alterna entre **mayor y menor** al tocarlo con el pulgar derecho. El pulgar tiene un punto verde y el índice uno blanco para visualizar la pinza que avanza la nota: C → D → E → F → G → A → B → C. La primera pinza pasa de C a D; mantenerla no repite el cambio. Separa los dedos antes de la siguiente acción.

Esta primera versión del modo acordes selecciona la tonalidad. El patrón de batería guardado sigue reproduciéndose y se conserva al volver a beat.

## Ejecutar

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Permite el acceso a la cámara si el sistema lo solicita. Pulsa **Q** para cerrar. Tras editar el código, cierra y vuelve a ejecutar el programa. El modelo de [MediaPipe Hand Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python) se descarga la primera vez. Las cuatro muestras WAV y su procedencia están en [assets/sounds/README.md](assets/sounds/README.md).

## Arquitectura

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | Declara qué marcadores y gestos se usan y qué acciones activan, como en `basic-impl`. |
| `camara/config.py` | Valores editables: manos, dedos, colores, BPM y umbrales. |
| `camara/tracker.py` | Convierte cada fotograma en manos y puntos normalizados. |
| `camara/detectors.py` | Implementa `put_dot`, `put_dot_if_raised`, `closest_touch` y el ángulo de la palma. |
| `camara/actions.py` | Acciones de los gestos y dibujo del panel, etiquetas e interruptores. |
| `camara/sequencer.py` | Guarda los patrones, los modos y el tempo; marca los pasos del bucle. |
| `camara/audio.py` | Carga las muestras y reproduce los golpes. |
| `camara/app.py` | Gestiona la webcam, el audio y el bucle de fotogramas. |

El flujo sigue el esquema de la rama `basic-impl`: webcam → `HandTracker` → `process_frame` en `main.py` → detectores y acciones → ventana. Para añadir un marcador, define su punto y color en `config.py` y añade una llamada a `put_dot` en `main.py`. Para añadir una interacción, detecta el gesto en `main.py` y define su efecto en `actions.py`; el estado musical persistente pertenece a `DrumMachine` en `sequencer.py`.

La detección de dedos se basa en puntos 2D: funciona mejor con la mano visible y orientada hacia la cámara. Si se pliega o gira, ajusta `EXTENDED_ANGLE_DEGREES` en `camara/config.py`. El slider calcula el ángulo en pantalla entre la muñeca y los nudillos, para que mover un dedo aislado no altere el BPM. El contacto usa `TOUCH_THRESHOLD` para los sonidos y `SLIDER_TOUCH_THRESHOLD` para el slider, medidos como proporción del tamaño de la palma. `CONFIRM_RELEASE_FRAMES` evita guardar varias veces por un solo contacto.

## Otras ramas

- `master`: índice y descripción general del proyecto.
- `basic-impl`: implementación básica y detectores reutilizables; puedes partir de ella para crear otra variante.
