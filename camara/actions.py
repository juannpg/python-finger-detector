"""Acciones de las pinzas y dibujo de la onda sobre la cámara."""

from __future__ import annotations

import cv2
import numpy as np

from camara.config import FREQUENCY, LINE_THICKNESS, POINT_RADIUS, PURPLE, WHITE
from camara.waveform import WaveformEditor


def add_breakpoint(frame: np.ndarray, editor: WaveformEditor, pinch: tuple[float, float] | None) -> None:
    height, width = frame.shape[:2]
    editor.add_at_pinch(pinch, width, height)


def move_breakpoint(frame: np.ndarray, editor: WaveformEditor, pinch: tuple[float, float] | None) -> None:
    height, width = frame.shape[:2]
    editor.drag_at_pinch(pinch, width, height)


def draw_waveform(frame: np.ndarray, editor: WaveformEditor) -> None:
    height, width = frame.shape[:2]
    xs = np.linspace(0, 1, width)
    ys = editor.waveform.sample(xs)
    pixels = np.column_stack((np.arange(width), np.rint(ys * (height - 1)))).astype(np.int32)
    cv2.polylines(frame, [pixels], False, PURPLE, LINE_THICKNESS, cv2.LINE_AA)

    for point in editor.waveform.points:
        center = (round(point.x * (width - 1)), round(point.y * (height - 1)))
        selected = point.id == editor.selected_id
        radius = POINT_RADIUS + (3 if selected else 0)
        cv2.circle(frame, center, radius + 2, WHITE, -1, cv2.LINE_AA)
        cv2.circle(frame, center, radius, PURPLE, -1, cv2.LINE_AA)
        if selected:
            cv2.circle(frame, center, 3, WHITE, -1, cv2.LINE_AA)

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width - 1, 64), (20, 18, 25), -1)
    cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, dst=frame)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f"UN CICLO  /  LA {FREQUENCY:g} Hz", (16, 25), font, 0.58, WHITE, 1, cv2.LINE_AA)
    cv2.putText(frame, "IZQ: crear punto   DER: mantener pinza y mover", (16, 49), font, 0.44, WHITE, 1, cv2.LINE_AA)
    footer = f"{len(editor.waveform.points)} puntos    R: reiniciar    Q: salir"
    cv2.putText(frame, footer, (16, height - 17), font, 0.45, (25, 20, 25), 3, cv2.LINE_AA)
    cv2.putText(frame, footer, (16, height - 17), font, 0.45, WHITE, 1, cv2.LINE_AA)
