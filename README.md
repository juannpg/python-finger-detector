# Cámara: interacción con las manos

Proyecto experimental de visión por computador para crear experiencias interactivas con gestos capturados por webcam.

## Esta rama: `drum-progression`

`drum-progression` construye un creador de patrones de batería sobre la base de `basic-impl`. La interfaz se controla con la mano derecha y convierte la postura de los dedos en un compás de cuatro tiempos que se reproduce en bucle a 80 BPM.

## Interacción prevista

| Dedo derecho | Papel |
| --- | --- |
| Pulgar | Círculo verde de confirmación. |
| Índice | Kick. |
| Medio | Snare. |
| Anular | Hihat. |
| Meñique | Splash. |

Los cuatro dedos blancos representan los cuatro tiempos del compás. Un dedo levantado escribe un `1` en su tiempo; uno bajado escribe un `0`, que representa silencio. Al acercar el pulgar verde a un instrumento se confirma su patrón.

Por ejemplo, al confirmar el índice se muestra en la esquina superior izquierda `kick: 1 0 1 1`. Los patrones confirmados se apilan en orden. Si se vuelve a confirmar un instrumento, su línea se reemplaza con el nuevo patrón en lugar de duplicarse. El tempo `80 BPM` se muestra en la esquina superior derecha.

## Ejecutar

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Concede permiso de cámara si se solicita y pulsa `Q` para cerrar. Además de las dependencias de visión, esta rama necesita los sonidos de kick, snare, hihat y splash para reproducir el patrón.

## Base técnica

La detección de manos, puntos de MediaPipe y reconocimiento de dedos procede de `basic-impl`. Esta rama añade la asignación de instrumentos, la captura de patrones de cuatro pasos, su visualización y la reproducción en bucle.

## Otras ramas

- `master`: índice y descripción general del proyecto.
- `basic-impl`: implementación básica, arquitectura y detectores reutilizables.
