"""Aquí se decide qué mostrar y qué gesto activa cada acción."""

import numpy as np

from camara.actions import write_straight_line
from camara.app import run
from camara.config import (
    GREEN, INDEX_TIP, MIDDLE_TIP, PINK, PINKY_TIP,
    RED, RING_PIP, RING_TIP, TARGET_HAND, THUMB_TIP, WHITE, WHITE_HAND,
)
from camara.detectors import on_touch, put_dot, put_dot_if_raised
from camara.tracker import Hand


def process_frame(frame: np.ndarray, hands: list[Hand], permanent_canvas: np.ndarray) -> None:
    for hand in hands:
        if hand.side == TARGET_HAND:
            put_dot(frame, hand, GREEN, INDEX_TIP)
            put_dot(frame, hand, RED, THUMB_TIP)
            put_dot(frame, hand, PINK, RING_PIP)

            on_touch(
                frame, hand, [RING_PIP, THUMB_TIP],
                lambda _: write_straight_line(permanent_canvas, hands),
            )
            on_touch(
                frame, hand, [THUMB_TIP, INDEX_TIP],
                lambda image: write_straight_line(image, hands),
            )

        if hand.side == WHITE_HAND:
            put_dot_if_raised(frame, hand, WHITE, THUMB_TIP)
            put_dot_if_raised(frame, hand, WHITE, INDEX_TIP)
            put_dot_if_raised(frame, hand, WHITE, MIDDLE_TIP)
            put_dot_if_raised(frame, hand, WHITE, RING_TIP)
            put_dot_if_raised(frame, hand, WHITE, PINKY_TIP)


if __name__ == "__main__":
    run(process_frame)
