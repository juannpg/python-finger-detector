# Cámara: dibujar el sonido con las manos

## Esta rama: `waveform-playground`

Un sintetizador que permite editar la forma de onda con la webcam. **Todo el ancho de la pantalla representa un único ciclo**, que se repite 440 veces por segundo: la frecuencia base de un La. Mover los puntos cambia la forma de ese ciclo y su timbre; también puede cambiar el volumen percibido. La posición horizontal de cada punto es su posición dentro del ciclo.

La experiencia empieza con una **línea morada horizontal en silencio**. El sonido aparece cuando desplazas un breakpoint y deformas la onda.

## Ejecutar

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

En la primera ejecución se descarga el modelo de [MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python) en `models/`. Se necesita permiso de cámara y una salida de audio disponible. Para cargar cambios en el código, cierra la ventana y vuelve a ejecutar `python main.py`.

## Controles

| Gesto o tecla | Acción |
| --- | --- |
| Pinzar con pulgar e índice **izquierdos** sobre la línea | Añade un breakpoint en la curva. Abre los dedos antes de añadir otro. |
| Pinzar con pulgar e índice **derechos** sobre un breakpoint | Lo agarra. Mantén la pinza y mueve la mano arriba o abajo para cambiar la onda. |
| Abrir la pinza derecha | Suelta el punto; la forma y el sonido se conservan. |
| `R` | Borra los puntos y restaura la línea plana y el silencio. |
| `Q` o cerrar la ventana | Termina la aplicación y el audio. |

El centro de la pinza es el punto medio entre las dos puntas de los dedos. Ambos dedos llevan marcadores blancos pequeños. El breakpoint seleccionado muestra un anillo mayor y un centro blanco. Durante el arrastre su posición horizontal permanece fija.

Los extremos de la curva permanecen en el centro de la pantalla. Las curvas pasan por todos los breakpoints con una tangente continua y unen ambos extremos suavemente al repetir el ciclo. El audio continúa aunque saques las manos de la cámara.

## Arquitectura

Se mantiene la estructura de `basic-impl`: configuración en un lugar, gestos conectados a acciones en `main.py` y recursos gestionados por el bucle de la aplicación.

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | Selecciona las manos, conecta cada detector de pinza con su acción y activa los marcadores. |
| `camara/config.py` | Manos, puntos, colores, márgenes, frecuencia y volumen. |
| `camara/tracker.py` | Convierte imágenes de MediaPipe en manos y coordenadas normalizadas. |
| `camara/detectors.py` | Detector reutilizable de pinza y función `put_dot`. |
| `camara/actions.py` | Acciones de añadir/mover y dibujo de la onda, breakpoints y textos. |
| `camara/waveform.py` | Forma del ciclo, interpolación y estado de las pinzas y del punto seleccionado. No depende de la cámara ni del audio. |
| `camara/audio.py` | Convierte la curva en una tabla de muestras y la reproduce continuamente. |
| `camara/app.py` | Abre/cierra cámara, detector, ventana y audio; ejecuta el bucle y procesa las teclas. |

El recorrido principal es: webcam → manos → detectores en `main.py` → acciones → estado de la onda → dibujo y audio.

### Valores que puedes editar

En `camara/config.py`:

- `ADD_HAND` y `DRAG_HAND`: conservan el mapeo observado en esta webcam en espejo (`Right` para la izquierda física y `Left` para la derecha).
- `PINCH_THRESHOLD` y `PINCH_RELEASE_THRESHOLD`: distancia de cierre y apertura, relativa al tamaño de la palma. El segundo umbral evita soltar y volver a agarrar por pequeñas variaciones del seguimiento.
- `LINE_HIT_RADIUS` y `POINT_HIT_RADIUS`: margen en píxeles para crear y agarrar puntos.
- `MIN_POINT_SPACING`: separación horizontal mínima entre breakpoints.
- `WAVE_TOP` y `WAVE_BOTTOM`: límites verticales del arrastre.
- `FREQUENCY`: ciclos por segundo; empieza en `440.0`.
- `AUDIO_GAIN`: ganancia de salida; empieza en `0.18`.
- `AUDIO_MORPH_SECONDS`: suavizado de los cambios de forma para reducir clics.

### Curva y síntesis

Las tangentes se calculan con [PCHIP de SciPy](https://docs.scipy.org/doc/scipy-1.13.1/reference/generated/scipy.interpolate.PchipInterpolator.html). Una [spline cúbica de Hermite](https://docs.scipy.org/doc/scipy-1.13.1/reference/generated/scipy.interpolate.CubicHermiteSpline.html) utiliza esas tangentes, fijando pendiente cero en ambos extremos para cerrar el ciclo.

Al cambiar la curva se genera una tabla de un período. Se elimina la componente continua y se descartan los armónicos por encima de la mitad de la frecuencia de muestreo. Un oscilador recorre esa tabla a 440 Hz, mantiene la fase entre bloques y suaviza las transiciones entre formas.

La salida usa un [OutputStream de sounddevice](https://python-sounddevice.readthedocs.io/en/0.5.3/api/streams.html). La interpolación de la curva y la FFT se hacen al editar la onda; el callback de audio interpola las muestras con buffers reutilizables, independientemente de los fotogramas de cámara.

## Pruebas sin webcam

```sh
python -m unittest discover -s tests -v
```

Comprueban creación y arrastre por pinzas, mapeo de manos, continuidad de la curva, silencio inicial, frecuencia de repetición, cambios de timbre y continuidad del audio entre bloques.

## Otras ramas

- `master`: índice y descripción general del proyecto.
- `basic-impl`: base de detección de manos, marcadores y gestos reutilizables.
- `drum-progression`: patrones de batería y selección de tonalidad por gestos.
