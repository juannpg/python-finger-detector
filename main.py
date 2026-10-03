"""Elige qué marcadores y gestos están activos en esta experiencia."""

import numpy as np

from camara.actions import (
    draw_instrument_label, draw_mode_switch, draw_status,
    handle_control_target, move_tempo_slider,
)
from camara.app import run
from camara.config import (
    BEAT_FINGERS, CHORD_CONTROL_TARGETS, CONTROL_HAND, CONTROL_TARGETS,
    GREEN, INDEX_TIP, INSTRUMENTS, INTERACTION_SWITCH_LANDMARK, KEY_QUALITY_LANDMARK,
    PATTERN_HAND, SLIDER_TARGET, SLIDER_TOUCH_THRESHOLD, THUMB_TIP, WHITE,
)
from camara.detectors import closest_touch, is_finger_raised, palm_rotation_degrees, put_dot
from camara.sequencer import DrumMachine
from camara.tracker import Hand


def process_frame(frame: np.ndarray, hands: list[Hand], machine: DrumMachine) -> None:
    pattern_hand = next((hand for hand in hands if hand.side == PATTERN_HAND), None)
    control_hand = next((hand for hand in hands if hand.side == CONTROL_HAND), None)

    pattern = None
    if pattern_hand is not None and machine.interaction_mode == "beat":
        pattern = tuple(
            int(is_finger_raised(frame, pattern_hand, tip))
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
        targets = CHORD_CONTROL_TARGETS if machine.interaction_mode == "chords" else CONTROL_TARGETS
        selected = closest_touch(frame, control_hand, THUMB_TIP, targets)

    handle_control_target(machine, selected, pattern)

    if machine.interaction_mode == "beat" and pattern_hand is not None and pattern is not None:
        for tip, raised in zip(BEAT_FINGERS, pattern):
            if raised:
                put_dot(frame, pattern_hand, WHITE, tip)
    if machine.interaction_mode == "beat" and control_hand is not None:
        for name, tip, color in INSTRUMENTS:
            put_dot(frame, control_hand, color, tip)
            draw_instrument_label(frame, control_hand, tip, name, color)

    draw_status(frame, machine)

    if pattern_hand is not None and machine.interaction_mode == "beat":
        draw_mode_switch(frame, pattern_hand, machine.slider_active)
        put_dot(frame, pattern_hand, WHITE, THUMB_TIP)
    if control_hand is not None:
        draw_mode_switch(
            frame, control_hand, machine.interaction_mode == "chords",
            INTERACTION_SWITCH_LANDMARK,
        )
        if machine.interaction_mode == "chords":
            draw_mode_switch(
                frame, control_hand, machine.key_quality == "minor", KEY_QUALITY_LANDMARK
            )
            quality = "menor" if machine.key_quality == "minor" else "mayor"
            draw_instrument_label(frame, control_hand, KEY_QUALITY_LANDMARK, quality, WHITE)
            put_dot(frame, control_hand, WHITE, INDEX_TIP)
            put_dot(frame, control_hand, GREEN, THUMB_TIP)
        else:
            draw_mode_switch(frame, control_hand, machine.mode == "eighth")
            put_dot(frame, control_hand, GREEN, THUMB_TIP)


if __name__ == "__main__":
    run(process_frame)
