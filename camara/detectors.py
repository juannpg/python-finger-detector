"""Funciones reutilizables para dibujar puntos y reaccionar a contactos."""

from collections.abc import Callable
from math import acos, degrees, hypot

import cv2
import numpy as np

from camara.config import (
    DOT_RADIUS, EXTENDED_ANGLE_DEGREES, FINGER_JOINTS,
    THUMB_TIP, TOUCH_THRESHOLD,
)
from camara.tracker import Hand, Point


def put_dot(frame: np.ndarray, hand: Hand, bgr: tuple[int, int, int], landmark: int) -> None:
    """Dibuja un punto de la mano sobre el fotograma."""
    height, width = frame.shape[:2]
    point = hand.points[landmark]
    x = int(point.x * width)
    y = int(point.y * height)
    cv2.circle(frame, (x, y), DOT_RADIUS, bgr, -1)


def _distance(a: Point, b: Point, width: int, height: int) -> float:
    return hypot((a.x - b.x) * width, (a.y - b.y) * height)


def _joint_angle(a: Point, joint: Point, b: Point, width: int, height: int) -> float:
    ax, ay = (a.x - joint.x) * width, (a.y - joint.y) * height
    bx, by = (b.x - joint.x) * width, (b.y - joint.y) * height
    lengths = hypot(ax, ay) * hypot(bx, by)
    if lengths == 0:
        return 0
    cosine = max(-1.0, min(1.0, (ax * bx + ay * by) / lengths))
    return degrees(acos(cosine))


def is_finger_raised(frame: np.ndarray, hand: Hand, fingertip: int) -> bool:
    """Aproxima si el dedo está extendido usando sus dos articulaciones en 2D."""
    base, middle, distal, tip = (hand.points[i] for i in FINGER_JOINTS[fingertip])
    height, width = frame.shape[:2]
    if _joint_angle(base, middle, distal, width, height) < EXTENDED_ANGLE_DEGREES:
        return False
    if _joint_angle(middle, distal, tip, width, height) < EXTENDED_ANGLE_DEGREES:
        return False

    if fingertip == THUMB_TIP:
        # Un pulgar recogido queda cerca de la base del meñique (punto 17).
        anchor = hand.points[17]
        return _distance(tip, anchor, width, height) > _distance(distal, anchor, width, height)

    wrist = hand.points[0]
    return _distance(tip, wrist, width, height) > _distance(middle, wrist, width, height)


def put_dot_if_raised(
    frame: np.ndarray, hand: Hand, bgr: tuple[int, int, int], fingertip: int
) -> None:
    """Dibuja la punta solo cuando el dedo está extendido."""
    if is_finger_raised(frame, hand, fingertip):
        put_dot(frame, hand, bgr, fingertip)


def on_touch(
    frame: np.ndarray,
    hand: Hand,
    pair: tuple[int, int],
    action: Callable[[np.ndarray], None],
) -> None:
    """Ejecuta la acción en cada fotograma donde los dos puntos se tocan."""
    height, width = frame.shape[:2]
    palm_size = _distance(hand.points[0], hand.points[9], width, height)
    if palm_size == 0:
        return
    gap = _distance(hand.points[pair[0]], hand.points[pair[1]], width, height)
    if gap < TOUCH_THRESHOLD * palm_size:
        action(frame)
