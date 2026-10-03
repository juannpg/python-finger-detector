"""Ajustes que normalmente querrás cambiar al experimentar."""

from pathlib import Path


CAMERA_INDEX = 0
MIRROR_IMAGE = True  # MediaPipe clasifica las manos suponiendo una imagen de espejo.
TARGET_HAND = "Left"
WHITE_HAND = "Right"
WINDOW_TITLE = "Camara - pulsa Q para salir"

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"


DOT_RADIUS = 12
# Colores BGR: OpenCV usa el orden azul, verde, rojo.
GREEN = (0, 255, 0)
RED = (0, 0, 255)
PINK = (100, 0, 255)
WHITE = (255, 255, 255)
LINE_THICKNESS = 3

# MediaPipe numera los 21 puntos de cada mano del 0 al 20.
INDEX_TIP = 8
INDEX_DIP = 7
THUMB_TIP = 4
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
RING_PIP = 14
# (base, articulación central, articulación distal, punta) de cada dedo.
FINGER_JOINTS = {
    THUMB_TIP: (1, 2, 3, THUMB_TIP),
    INDEX_TIP: (5, 6, 7, INDEX_TIP),
    MIDDLE_TIP: (9, 10, 11, MIDDLE_TIP),
    RING_TIP: (13, 14, 15, RING_TIP),
    PINKY_TIP: (17, 18, 19, PINKY_TIP),
}
# Un dedo se considera extendido si sus dos articulaciones forman al menos este ángulo.
EXTENDED_ANGLE_DEGREES = 155
# Distancia máxima entre los puntos, como fracción del tamaño de la palma.
TOUCH_THRESHOLD = 0.20
