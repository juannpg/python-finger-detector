"""Ajustes que normalmente querrás cambiar al experimentar."""

from pathlib import Path


CAMERA_INDEX = 0
MIRROR_IMAGE = True  # MediaPipe clasifica las manos suponiendo una imagen de espejo.
# Etiquetas observadas con esta webcam en espejo: la izquierda física sale "Right".
PATTERN_HAND = "Right"  # Meñique, anular, medio e índice = tiempos 1 a 4.
CONTROL_HAND = "Left"   # Pulgar = confirmar; otros dedos = instrumentos.
WINDOW_TITLE = "Camara - pulsa Q para salir"
BPM = 80
SLIDER_MIN_BPM = 40
SLIDER_MAX_BPM = 180
SLIDER_BPM_PER_DEGREE = 1.5
SLIDER_ANGLE_DEADZONE = 2.0
SLIDER_SMOOTHING = 0.25

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"


DOT_RADIUS = 12
# Colores BGR: OpenCV usa el orden azul, verde, rojo.
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PURPLE = (210, 75, 150)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
HIHAT_COLOR = (0, 255, 255)
SPLASH_COLOR = (255, 0, 255)

# MediaPipe numera los 21 puntos de cada mano del 0 al 20.
INDEX_TIP = 8
THUMB_TIP = 4
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
BEAT_FINGERS = (PINKY_TIP, RING_TIP, MIDDLE_TIP, INDEX_TIP)
MODE_SWITCH_LANDMARK = 17  # Nudillo de la base del meñique de cada mano.
INTERACTION_SWITCH_LANDMARK = 13  # Base del anular derecho: beat/acordes.
KEY_QUALITY_LANDMARK = MIDDLE_TIP  # Punta del medio derecho: mayor/menor.
KEY_NOTES = ("C", "D", "E", "F", "G", "A", "B")
# (nombre, punta que confirma el sonido, color BGR)
INSTRUMENTS = (
    ("kick", INDEX_TIP, (255, 0, 0)),
    ("snare", MIDDLE_TIP, RED),
    ("hihat", RING_TIP, HIHAT_COLOR),
    ("splash", PINKY_TIP, SPLASH_COLOR),
)
MODE_TARGET = "mode"
INTERACTION_TARGET = "interaction"
KEY_QUALITY_TARGET = "key_quality"
KEY_NOTE_TARGET = "key_note"
CONTROL_TARGETS = tuple((name, tip) for name, tip, _ in INSTRUMENTS) + (
    (MODE_TARGET, MODE_SWITCH_LANDMARK),
    (INTERACTION_TARGET, INTERACTION_SWITCH_LANDMARK),
)
CHORD_CONTROL_TARGETS = (
    (INTERACTION_TARGET, INTERACTION_SWITCH_LANDMARK),
    (KEY_QUALITY_TARGET, KEY_QUALITY_LANDMARK),
    (KEY_NOTE_TARGET, INDEX_TIP),
)
SLIDER_TARGET = (("slider", MODE_SWITCH_LANDMARK),)
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
SLIDER_TOUCH_THRESHOLD = 0.25
CONFIRM_RELEASE_FRAMES = 3
