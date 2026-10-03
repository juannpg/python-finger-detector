"""Un ciclo de onda y el estado de sus breakpoints, independiente de la webcam."""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import hypot

import numpy as np
from scipy.interpolate import CubicHermiteSpline, PchipInterpolator

from camara.config import (
    LINE_HIT_RADIUS, MIN_POINT_SPACING, POINT_HIT_RADIUS,
    WAVE_BOTTOM, WAVE_CENTER, WAVE_TOP,
)


@dataclass(frozen=True)
class Breakpoint:
    id: int
    x: float
    y: float


class Waveform:
    def __init__(self) -> None:
        self._points: list[Breakpoint] = []
        self._next_id = 0
        self.revision = 0
        self._rebuild()

    @property
    def points(self) -> tuple[Breakpoint, ...]:
        return tuple(self._points)

    def sample(self, positions: float | np.ndarray) -> np.ndarray:
        return self._curve(positions)

    def _rebuild(self) -> None:
        xs = np.array([0.0, *(point.x for point in self._points), 1.0])
        ys = np.array([WAVE_CENTER, *(point.y for point in self._points), WAVE_CENTER])
        # PCHIP evita desbordamientos. Hermite comparte tangente en cada punto
        # y une el ciclo por sus extremos con pendiente cero.
        slopes = PchipInterpolator(xs, ys).derivative()(xs)
        slopes[0] = slopes[-1] = 0.0
        self._curve = CubicHermiteSpline(xs, ys, slopes)
        self.revision += 1

    def add_point(self, x: float) -> Breakpoint | None:
        if not MIN_POINT_SPACING <= x <= 1 - MIN_POINT_SPACING:
            return None
        if any(abs(point.x - x) < MIN_POINT_SPACING for point in self._points):
            return None
        point = Breakpoint(self._next_id, x, float(self.sample(x)))
        self._next_id += 1
        self._points.append(point)
        self._points.sort(key=lambda item: item.x)
        self._rebuild()
        return point

    def move_point(self, point_id: int, y: float) -> None:
        y = max(WAVE_TOP, min(WAVE_BOTTOM, y))
        for index, point in enumerate(self._points):
            if point.id == point_id:
                if abs(point.y - y) > 1e-6:
                    self._points[index] = replace(point, y=y)
                    self._rebuild()
                return

    def reset(self) -> None:
        self._points.clear()
        self._rebuild()


class WaveformEditor:
    def __init__(self) -> None:
        self.waveform = Waveform()
        self.left_pinched = False
        self.right_pinched = False
        self.selected_id: int | None = None
        self._drag_offset_y = 0.0

    def add_at_pinch(self, pinch: tuple[float, float] | None, width: int, height: int) -> None:
        started = pinch is not None and not self.left_pinched
        self.left_pinched = pinch is not None
        if not started:
            return
        x, y = pinch
        if not 0 <= x <= 1 or not 0 <= y <= 1:
            return
        # Buscar la curva en píxeles permite acertar también en tramos inclinados.
        xs = np.linspace(0, 1, max(width, 2))
        ys = self.waveform.sample(xs)
        distances = ((xs - x) * (width - 1)) ** 2 + ((ys - y) * (height - 1)) ** 2
        closest = int(np.argmin(distances))
        if distances[closest] <= LINE_HIT_RADIUS ** 2:
            self.waveform.add_point(float(xs[closest]))

    def drag_at_pinch(self, pinch: tuple[float, float] | None, width: int, height: int) -> None:
        if pinch is None:
            self.right_pinched = False
            self.selected_id = None
            return
        x, y = pinch
        if not self.right_pinched:
            self.right_pinched = True
            nearest = min(
                self.waveform.points,
                key=lambda point: hypot((point.x - x) * (width - 1), (point.y - y) * (height - 1)),
                default=None,
            )
            if nearest is not None:
                gap = hypot((nearest.x - x) * (width - 1), (nearest.y - y) * (height - 1))
                if gap <= POINT_HIT_RADIUS:
                    self.selected_id = nearest.id
                    self._drag_offset_y = nearest.y - y
        if self.selected_id is not None:
            self.waveform.move_point(self.selected_id, y + self._drag_offset_y)

    def reset(self) -> None:
        self.waveform.reset()
        self.selected_id = None
        # Una pinza mantenida no vuelve a crear un punto tras pulsar R.
