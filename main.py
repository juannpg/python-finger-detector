"""Elige qué marcadores y gestos están activos en esta experiencia."""

import numpy as np

from camara.actions import (
    draw_instrument_label, draw_mode_switch, draw_status,
    handle_control_target, move_tempo_slider,
)
from camara.app import run
from camara.config import (
    BEAT_FINGERS, CONTROL_HAND, CONTROL_TARGETS, GREEN, INSTRUMENTS,
    PATTERN_HAND, SLIDER_TARGET, SLIDER_TOUCH_THRESHOLD, THUMB_TIP, WHITE,
)
from camara.detectors import closest_touch, palm_rotation_degrees, put_dot, put_dot_if_raised
from camara.sequencer import DrumMachine
from camara.tracker import Hand


def process_frame(frame: np.ndarray, hands: list[Hand], machine: DrumMachine) -> None:
    pattern_hand = next((hand for hand in hands if hand.side == PATTERN_HAND), None)
    control_hand = next((hand for hand in hands if hand.side == CONTROL_HAND), None)

    pattern = None
    if pattern_hand is not None:
        pattern = tuple(
            int(put_dot_if_raised(frame, pattern_hand, WHITE, tip))
            for tip in BEAT_FINGERS
        )
        slider_pressed = closest_touch(
            frame, pattern_hand, THUMB_TIP, SLIDER_TARGET,
            threshold=SLIDER_TOUCH_THRESHOLD,
        ) is not None
        move_tempo_slider(
            machine, slider_pressed, palm_rotation_degrees(frame, pattern_hand)
        )
    else:
        move_tempo_slider(machine, False, None)

    selected = None
    if control_hand is not None:
        for name, tip, color in INSTRUMENTS:
            put_dot(frame, control_hand, color, tip)
            draw_instrument_label(frame, control_hand, tip, name, color)
        selected = closest_touch(frame, control_hand, THUMB_TIP, CONTROL_TARGETS)

    handle_control_target(machine, selected, pattern)
    draw_status(frame, machine)

    if pattern_hand is not None:
        draw_mode_switch(frame, pattern_hand, machine.slider_active)
        put_dot(frame, pattern_hand, WHITE, THUMB_TIP)
    if control_hand is not None:
        draw_mode_switch(frame, control_hand, machine.mode == "eighth")
        put_dot(frame, control_hand, GREEN, THUMB_TIP)


if __name__ == "__main__":
    run(process_frame)
