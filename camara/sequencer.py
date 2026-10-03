"""Estado de patrones y reloj de cuatro tiempos con ocho subdivisiones."""

from __future__ import annotations

from collections.abc import Callable
from time import monotonic

from camara.config import (
    BPM, CONFIRM_RELEASE_FRAMES, INSTRUMENTS, SLIDER_ANGLE_DEADZONE,
    SLIDER_BPM_PER_DEGREE, SLIDER_MAX_BPM, SLIDER_MIN_BPM, SLIDER_SMOOTHING,
)


FourBeats = tuple[int, int, int, int]
Pattern = tuple[int, ...]


class DrumMachine:
    def __init__(
        self, play: Callable[[str], None], bpm: int = BPM, start_at: float | None = None
    ) -> None:
        self.bpm = bpm
        self.mode = "quarter"
        self.patterns: dict[str, Pattern] = {
            name: (0, 0, 0, 0) for name, _, _ in INSTRUMENTS
        }
        self._next_eighth_half = {name: 0 for name in self.patterns}
        self._play = play
        self._step = 0
        self._next_step_at = monotonic() if start_at is None else start_at
        self._active_contact: str | None = None
        self._release_frames = 0
        self.slider_active = False
        self._slider_reference_angle = 0.0
        self._slider_reference_bpm = bpm
        self._slider_smoothed_bpm = float(bpm)

    def confirm(
        self,
        instrument: str | None,
        pattern: FourBeats | None,
    ) -> None:
        """Confirma un sonido en el modo actual y evita repetirlo durante el contacto."""
        if instrument is None:
            self._release_frames += 1
            if self._release_frames >= CONFIRM_RELEASE_FRAMES:
                self._active_contact = None
            return

        self._release_frames = 0
        if pattern is None or self._active_contact is not None:
            return

        if self.mode == "quarter":
            self.patterns[instrument] = pattern
            self._next_eighth_half[instrument] = 0
        else:
            current = self.patterns[instrument]
            if len(current) == 4:
                current = (0,) * 8
                self._next_eighth_half[instrument] = 0
            half = self._next_eighth_half[instrument]
            notes = list(current)
            notes[half * 4 : half * 4 + 4] = pattern
            self.patterns[instrument] = tuple(notes)
            self._next_eighth_half[instrument] = 1 - half

        self._active_contact = instrument

    def toggle_mode(self) -> None:
        """Alterna el modo una vez por contacto con el interruptor."""
        self._release_frames = 0
        if self._active_contact is not None:
            return
        self.mode = "eighth" if self.mode == "quarter" else "quarter"
        self._active_contact = "mode"

    def update_slider(self, touching: bool, angle_degrees: float | None) -> None:
        """Ajusta el tempo solo mientras el pulgar mantiene pulsado el punto."""
        if not touching or angle_degrees is None:
            self.slider_active = False
            return
        if not self.slider_active:
            self.slider_active = True
            self._slider_reference_angle = angle_degrees
            self._slider_reference_bpm = self.bpm
            self._slider_smoothed_bpm = float(self.bpm)

        movement = (
            angle_degrees - self._slider_reference_angle + 180
        ) % 360 - 180
        if abs(movement) < SLIDER_ANGLE_DEADZONE:
            movement = 0.0
        target = self._slider_reference_bpm + movement * SLIDER_BPM_PER_DEGREE
        target = max(SLIDER_MIN_BPM, min(SLIDER_MAX_BPM, target))
        self._slider_smoothed_bpm += SLIDER_SMOOTHING * (
            target - self._slider_smoothed_bpm
        )
        self.bpm = round(self._slider_smoothed_bpm)

    def tick(self, now: float | None = None) -> None:
        """Reproduce el tiempo que toca sin acumular golpes si se retrasa la cámara."""
        if now is None:
            now = monotonic()
        if now < self._next_step_at:
            return

        seconds_per_step = 60 / self.bpm / 2
        elapsed_steps = int((now - self._next_step_at) / seconds_per_step) + 1
        current_step = (self._step + elapsed_steps - 1) % 8
        for instrument, pattern in self.patterns.items():
            should_play = (
                pattern[current_step]
                if len(pattern) == 8
                else current_step % 2 == 0 and pattern[current_step // 2]
            )
            if should_play:
                self._play(instrument)

        self._step = (current_step + 1) % 8
        self._next_step_at += elapsed_steps * seconds_per_step
