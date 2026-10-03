"""Marcadores y gestos reutilizables para configurar la experiencia en main."""

from __future__ import annotations

from math import acos, atan2, degrees, hypot
from typing import Sequence, TypeVar

import cv2
import numpy as np

from camara.config import (
    BEAT_FINGERS, DOT_RADIUS, EXTENDED_ANGLE_DEGREES, FINGER_JOINTS,
    THUMB_TIP, TOUCH_THRESHOLD,
)
from camara.tracker import Hand, Point


def put_dot(
    frame: np.ndarray,
    hand: Hand,
    bgr: tuple[int, int, int],
    landmark: int,
    radius: int = DOT_RADIUS,
) -> None:
    """Dibuja un punto en cualquier marcador de MediaPipe."""
    height, width = frame.shape[:2]
    point = hand.points[landmark]
    cv2.circle(frame, (int(point.x * width), int(point.y * height)), radius, bgr, -1)


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
) -> bool:
    """Dibuja el punto si el dedo está levantado y devuelve ese estado."""
    raised = is_finger_raised(frame, hand, fingertip)
    if raised:
        put_dot(frame, hand, bgr, fingertip)
    return raised


def palm_rotation_degrees(frame: np.ndarray, hand: Hand) -> float:
    """Ángulo de la palma en pantalla: positivo al girar hacia la derecha."""
    wrist = hand.points[0]
    bases = [hand.points[FINGER_JOINTS[tip][0]] for tip in BEAT_FINGERS]
    center_x = sum(point.x for point in bases) / len(bases)
    center_y = sum(point.y for point in bases) / len(bases)
    height, width = frame.shape[:2]
    return degrees(atan2((center_x - wrist.x) * width, (wrist.y - center_y) * height))


Choice = TypeVar("Choice")


def closest_touch(
    frame: np.ndarray,
    hand: Hand,
    anchor: int,
    candidates: Sequence[tuple[Choice, int]],
    threshold: float = TOUCH_THRESHOLD,
) -> Choice | None:
    """Devuelve el dedo más cercano al pulgar si está dentro del umbral."""
    height, width = frame.shape[:2]
    palm_size = _distance(hand.points[0], hand.points[9], width, height)
    if palm_size == 0:
        return None

    distances = (
        (_distance(hand.points[anchor], hand.points[tip], width, height), name)
        for name, tip in candidates
    )
    gap, choice = min(distances, key=lambda item: item[0])
    return choice if gap < threshold * palm_size else None
