"""Valores editables de la experiencia de síntesis con breakpoints."""

from pathlib import Path

CAMERA_INDEX = 0
MIRROR_IMAGE = True
# Etiquetas observadas en esta webcam: izquierda física = Right.
ADD_HAND = "Right"
DRAG_HAND = "Left"
WINDOW_TITLE = "Onda - R reiniciar - Q salir"

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"

THUMB_TIP = 4
INDEX_TIP = 8
ACTION_FINGERS = (THUMB_TIP, INDEX_TIP)
PINCH_THRESHOLD = 0.20  # Proporción de la distancia muñeca-nudillo medio.
PINCH_RELEASE_THRESHOLD = 0.28
LINE_HIT_RADIUS = 22  # Píxeles: margen para añadir sobre la curva.
POINT_HIT_RADIUS = 26
MIN_POINT_SPACING = 0.025  # Proporción del ancho de la pantalla.
WAVE_TOP = 0.15
WAVE_BOTTOM = 0.90
WAVE_CENTER = 0.50

# Colores BGR de OpenCV.
PURPLE = (220, 90, 170)
WHITE = (255, 255, 255)
DOT_RADIUS = 5
POINT_RADIUS = 8
LINE_THICKNESS = 3

FREQUENCY = 440.0
SAMPLE_RATE = 48000
TABLE_SIZE = 2048
AUDIO_BLOCK_SIZE = 256
AUDIO_GAIN = 0.18
AUDIO_MORPH_SECONDS = 0.025
