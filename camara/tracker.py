"""Convierte fotogramas en posiciones normalizadas de las manos."""

from dataclasses import dataclass
from time import monotonic_ns
from urllib.request import urlretrieve

import cv2
import mediapipe as mp
import numpy as np

from camara.config import MIRROR_IMAGE, MODEL_PATH, MODEL_URL


@dataclass(frozen=True)
class Point:
    x: float  # Entre 0 y 1: proporción del ancho de la imagen.
    y: float  # Entre 0 y 1: proporción del alto de la imagen.


@dataclass(frozen=True)
class Hand:
    side: str  # "Right" o "Left".
    points: tuple[Point, ...]


def ensure_model() -> None:
    if MODEL_PATH.exists():
        return
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    print("Descargando el modelo de detección de manos...")
    urlretrieve(MODEL_URL, MODEL_PATH)


class HandTracker:
    def __init__(self) -> None:
        ensure_model()
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=2,
        )
        self._detector = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self._last_timestamp_ms = -1

    def detect(self, frame: np.ndarray) -> list[Hand]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = max(monotonic_ns() // 1_000_000, self._last_timestamp_ms + 1)
        self._last_timestamp_ms = timestamp_ms
        result = self._detector.detect_for_video(image, timestamp_ms)

        hands = []
        for landmarks, handedness in zip(result.hand_landmarks, result.handedness):
            side = handedness[0].category_name
            if not MIRROR_IMAGE:
                side = "Left" if side == "Right" else "Right"
            hands.append(
                Hand(
                    side=side,
                    points=tuple(Point(point.x, point.y) for point in landmarks),
                )
            )
        return hands

    def close(self) -> None:
        self._detector.close()

    def __enter__(self) -> "HandTracker":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
