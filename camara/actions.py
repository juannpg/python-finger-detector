"""Acciones que pueden disparar los detectores."""

import cv2
import numpy as np

from camara.config import (
    INDEX_TIP, LINE_THICKNESS, MIDDLE_TIP, PINKY_TIP,
    RING_TIP, THUMB_TIP, WHITE, WHITE_HAND,
)
from camara.detectors import is_finger_raised
from camara.tracker import Hand


def write_straight_line(frame: np.ndarray, hands: list[Hand]) -> None:
    """Une las puntas blancas que están levantadas, en orden de pulgar a meñique."""
    height, width = frame.shape[:2]
    fingertips = (THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP)

    for hand in hands:
        if hand.side != WHITE_HAND:
            continue

        raised = [tip for tip in fingertips if is_finger_raised(frame, hand, tip)]
        for first, second in zip(raised, raised[1:]):
            a, b = hand.points[first], hand.points[second]
            start = (int(a.x * width), int(a.y * height))
            end = (int(b.x * width), int(b.y * height))
            cv2.line(frame, start, end, WHITE, LINE_THICKNESS, cv2.LINE_AA)
