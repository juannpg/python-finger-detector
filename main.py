"""Configura los marcadores y conecta las pinzas con sus acciones."""

import numpy as np

from camara.actions import add_breakpoint, draw_waveform, move_breakpoint
from camara.app import run
from camara.config import ACTION_FINGERS, ADD_HAND, DRAG_HAND, WHITE
from camara.detectors import pinch_position, put_dot
from camara.tracker import Hand
from camara.waveform import WaveformEditor


def process_frame(frame: np.ndarray, hands: list[Hand], editor: WaveformEditor) -> None:
    left = next((hand for hand in hands if hand.side == ADD_HAND), None)
    right = next((hand for hand in hands if hand.side == DRAG_HAND), None)

    add_breakpoint(frame, editor, pinch_position(frame, left, editor.left_pinched))
    move_breakpoint(frame, editor, pinch_position(frame, right, editor.right_pinched))
    draw_waveform(frame, editor)

    for hand in (left, right):
        if hand is not None:
            for fingertip in ACTION_FINGERS:
                put_dot(frame, hand, WHITE, fingertip)


if __name__ == "__main__":
    run(process_frame)
