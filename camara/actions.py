"""Acciones de los gestos y dibujo de la interfaz."""

from __future__ import annotations

import cv2
import numpy as np

from camara.config import (
    BLACK, DOT_RADIUS, INSTRUMENTS, INTERACTION_TARGET, KEY_NOTE_TARGET,
    KEY_QUALITY_TARGET, MODE_SWITCH_LANDMARK, MODE_TARGET,
    PURPLE, WHITE,
)
from camara.sequencer import DrumMachine, FourBeats
from camara.tracker import Hand


def move_tempo_slider(
    machine: DrumMachine, touching: bool, angle_degrees: float | None
) -> None:
    """Usa el giro de la mano para cambiar el BPM mientras el punto está pulsado."""
    machine.update_slider(touching, angle_degrees)


def handle_control_target(
    machine: DrumMachine, target: str | None, pattern: FourBeats | None
) -> None:
    """El punto seleccionado confirma un sonido o cambia negras/corcheas."""
    if target is None:
        machine.confirm(None, None)
    elif target == MODE_TARGET:
        machine.toggle_mode()
    elif target == INTERACTION_TARGET:
        machine.toggle_interaction_mode()
    elif target == KEY_QUALITY_TARGET:
        machine.toggle_key_quality()
    elif target == KEY_NOTE_TARGET:
        machine.advance_key()
    else:
        machine.confirm(target, pattern)


def draw_instrument_label(
    frame: np.ndarray, hand: Hand, fingertip: int, name: str, color: tuple[int, int, int]
) -> None:
    height, width = frame.shape[:2]
    point = hand.points[fingertip]
    x = min(int(point.x * width) + 16, width - 1)
    y = max(int(point.y * height) - 10, 16)
    cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)


def draw_mode_switch(
    frame: np.ndarray, hand: Hand, active: bool, landmark: int = MODE_SWITCH_LANDMARK
) -> None:
    height, width = frame.shape[:2]
    point = hand.points[landmark]
    center = (int(point.x * width), int(point.y * height))
    cv2.circle(frame, center, DOT_RADIUS + 2, WHITE, -1)
    cv2.circle(frame, center, DOT_RADIUS, PURPLE if active else BLACK, -1)


def _draw_centered_label(frame: np.ndarray, message: str, y: int) -> None:
    font, scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
    (width, height), baseline = cv2.getTextSize(message, font, scale, thickness)
    x = (frame.shape[1] - width) // 2
    cv2.rectangle(frame, (x - 12, y - height - 6), (x + width + 12, y + baseline + 6), (25, 25, 25), -1)
    cv2.putText(frame, message, (x, y), font, scale, WHITE, thickness)


def draw_status(frame: np.ndarray, machine: DrumMachine) -> None:
    height, width = frame.shape[:2]
    tempo = f"{machine.bpm} BPM"
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, _), _ = cv2.getTextSize(tempo, font, 0.7, 2)
    badge_x = max(8, width - text_width - 28)
    cv2.rectangle(frame, (badge_x - 8, 8), (width - 12, 42), (30, 30, 30), -1)
    tempo_color = PURPLE if machine.slider_active else WHITE
    cv2.putText(frame, tempo, (badge_x, 33), font, 0.7, tempo_color, 2)

    message = "modo: corcheas" if machine.mode == "eighth" else "modo: negras"
    mode_scale = 0.8 if width >= 600 else 0.6
    mode_y = 72 if width < 420 else 33
    (message_width, message_height), baseline = cv2.getTextSize(
        message, font, mode_scale, 2
    )
    mode_x = (width - message_width) // 2
    cv2.rectangle(
        frame,
        (mode_x - 14, mode_y - message_height - 8),
        (mode_x + message_width + 14, mode_y + baseline + 8),
        (25, 25, 25),
        -1,
    )
    mode_color = PURPLE if machine.mode == "eighth" else WHITE
    cv2.putText(frame, message, (mode_x, mode_y), font, mode_scale, mode_color, 2)

    interaction = "acordes" if machine.interaction_mode == "chords" else "beat"
    quality = "menor" if machine.key_quality == "minor" else "mayor"
    key = f"{machine.key_note} {quality}"
    _draw_centered_label(frame, f"modo: {interaction}", mode_y + 36)
    _draw_centered_label(frame, f"tonalidad: {key}", mode_y + 72)

    panel_x, panel_y = 12, mode_y + 98
    panel_width = min(520, width - 24)
    panel_height = 192
    if panel_width <= 0 or height <= panel_y:
        return
    panel_bottom = min(panel_y + panel_height, height - 1)
    overlay = frame.copy()
    cv2.rectangle(
        overlay, (panel_x, panel_y), (panel_x + panel_width, panel_bottom), (18, 18, 18), -1
    )
    cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, dst=frame)
    cv2.rectangle(
        frame, (panel_x, panel_y), (panel_x + panel_width, panel_bottom), (100, 100, 100), 1
    )

    label_width = min(150, int(panel_width * 0.30))
    grid_left = panel_x + label_width
    grid_right = panel_x + panel_width - 25
    step = (grid_right - grid_left) / 7
    number_scale = 0.8 if width >= 520 else 0.62
    for column, heading in enumerate(("1", "&", "2", "&", "3", "&", "4", "&")):
        x = round(grid_left + column * step)
        cv2.putText(frame, heading, (x, panel_y + 22), font, 0.48, (175, 175, 175), 1)

    colors = {name: color for name, _, color in INSTRUMENTS}
    for row, (instrument, pattern) in enumerate(machine.patterns.items()):
        y = panel_y + 59 + row * 36
        if y >= height:
            break
        cv2.putText(frame, f"{instrument}:", (panel_x + 14, y), font, 0.7, colors[instrument], 2)
        columns = range(8) if len(pattern) == 8 else range(0, 8, 2)
        for note, column in zip(pattern, columns):
            x = round(grid_left + column * step)
            color = WHITE if note else (155, 155, 155)
            cv2.putText(frame, str(note), (x, y), font, number_scale, color, 2)
