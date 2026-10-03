"""Marcadores y detector de pinza reutilizable, sin reglas de la onda."""

from __future__ import annotations

from math import hypot

import cv2
import numpy as np

from camara.config import DOT_RADIUS, INDEX_TIP, PINCH_RELEASE_THRESHOLD, PINCH_THRESHOLD, THUMB_TIP
from camara.tracker import Hand


def put_dot(frame: np.ndarray, hand: Hand, bgr: tuple[int, int, int], landmark: int) -> None:
    height, width = frame.shape[:2]
    point = hand.points[landmark]
    center = (round(point.x * (width - 1)), round(point.y * (height - 1)))
    cv2.circle(frame, center, DOT_RADIUS + 1, (35, 35, 35), -1, cv2.LINE_AA)
    cv2.circle(frame, center, DOT_RADIUS, bgr, -1, cv2.LINE_AA)


def pinch_position(
    frame: np.ndarray, hand: Hand | None, was_pinched: bool
) -> tuple[float, float] | None:
    """Devuelve el centro pulgar-índice mientras se mantiene la pinza."""
    if hand is None:
        return None
    height, width = frame.shape[:2]
    wrist, knuckle = hand.points[0], hand.points[9]
    palm = hypot((wrist.x - knuckle.x) * width, (wrist.y - knuckle.y) * height)
    if palm < 1:
        return None
    thumb, index = hand.points[THUMB_TIP], hand.points[INDEX_TIP]
    gap = hypot((thumb.x - index.x) * width, (thumb.y - index.y) * height)
    threshold = PINCH_RELEASE_THRESHOLD if was_pinched else PINCH_THRESHOLD
    if gap >= threshold * palm:
        return None
    return ((thumb.x + index.x) / 2, (thumb.y + index.y) / 2)
