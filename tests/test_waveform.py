import unittest

import numpy as np

from camara.config import MIN_POINT_SPACING, WAVE_BOTTOM, WAVE_CENTER, WAVE_TOP
from camara.waveform import Waveform, WaveformEditor


class WaveformTests(unittest.TestCase):
    def test_starts_flat_and_reset_restores_flat_line(self):
        wave = Waveform()
        xs = np.linspace(0, 1, 1000)
        np.testing.assert_array_equal(wave.sample(xs), np.full_like(xs, WAVE_CENTER))
        point = wave.add_point(0.3)
        wave.move_point(point.id, 0.2)
        self.assertGreater(np.ptp(wave.sample(xs)), 0.2)
        wave.reset()
        self.assertEqual(wave.points, ())
        np.testing.assert_array_equal(wave.sample(xs), np.full_like(xs, WAVE_CENTER))

    def test_curve_passes_through_points_and_has_continuous_tangents(self):
        wave = Waveform()
        for x, y in ((0.2, 0.25), (0.4, 0.35), (0.6, 0.8), (0.8, 0.3)):
            point = wave.add_point(x)
            wave.move_point(point.id, y)
        epsilon = 1e-6
        for point in wave.points:
            self.assertAlmostEqual(float(wave.sample(point.x)), point.y)
            left = (wave.sample(point.x) - wave.sample(point.x - epsilon)) / epsilon
            right = (wave.sample(point.x + epsilon) - wave.sample(point.x)) / epsilon
            self.assertAlmostEqual(float(left), float(right), delta=0.0002)
        self.assertAlmostEqual(float(wave.sample(0)), float(wave.sample(1)))
        start_slope = (wave.sample(epsilon) - wave.sample(0)) / epsilon
        end_slope = (wave.sample(1) - wave.sample(1 - epsilon)) / epsilon
        self.assertAlmostEqual(float(start_slope), 0, delta=0.0002)
        self.assertAlmostEqual(float(end_slope), 0, delta=0.0002)
        ys = wave.sample(np.linspace(0, 1, 10000))
        self.assertGreaterEqual(ys.min(), 0.25 - 1e-8)
        self.assertLessEqual(ys.max(), 0.8 + 1e-8)

    def test_spacing_and_vertical_limits(self):
        wave = Waveform()
        point = wave.add_point(0.5)
        for x in (0, 1, 0.5, 0.5 + MIN_POINT_SPACING / 2):
            self.assertIsNone(wave.add_point(x))
        wave.move_point(point.id, -1)
        self.assertEqual(wave.points[0].y, WAVE_TOP)
        wave.move_point(point.id, 2)
        self.assertEqual(wave.points[0].y, WAVE_BOTTOM)
        self.assertEqual(wave.points[0].x, 0.5)


class GestureTests(unittest.TestCase):
    def setUp(self):
        self.editor = WaveformEditor()
        self.size = (1001, 601)

    def test_left_pinch_adds_once_and_only_on_curve(self):
        self.editor.add_at_pinch((0.3, 0.5), *self.size)
        self.editor.add_at_pinch((0.6, 0.5), *self.size)
        self.assertEqual(len(self.editor.waveform.points), 1)
        self.editor.add_at_pinch(None, *self.size)
        self.editor.add_at_pinch((0.6, 0.2), *self.size)
        self.editor.add_at_pinch((0.6, 0.5), *self.size)
        self.assertEqual(len(self.editor.waveform.points), 1)
        self.editor.add_at_pinch(None, *self.size)
        self.editor.add_at_pinch((0.6, 0.5), *self.size)
        self.assertEqual(len(self.editor.waveform.points), 2)

    def test_add_snaps_to_the_current_curve(self):
        point = self.editor.waveform.add_point(0.5)
        self.editor.waveform.move_point(point.id, 0.2)
        x = 0.25
        y = float(self.editor.waveform.sample(x))
        self.editor.add_at_pinch((x, y + 0.01), *self.size)
        points = self.editor.waveform.points
        self.assertEqual(len(points), 2)
        self.assertLess(abs(points[0].x - x), 0.02)
        self.assertAlmostEqual(float(self.editor.waveform.sample(points[0].x)), points[0].y)

    def test_right_drag_keeps_x_preserves_grab_offset_and_releases(self):
        point = self.editor.waveform.add_point(0.5)
        self.editor.drag_at_pinch((0.51, 0.52), *self.size)
        self.assertEqual(self.editor.selected_id, point.id)
        self.assertAlmostEqual(self.editor.waveform.points[0].y, 0.5)
        self.editor.drag_at_pinch((0.8, 0.32), *self.size)
        moved = self.editor.waveform.points[0]
        self.assertEqual(moved.x, 0.5)
        self.assertAlmostEqual(moved.y, 0.3)
        self.editor.drag_at_pinch(None, *self.size)
        self.assertIsNone(self.editor.selected_id)
        self.editor.drag_at_pinch((0.8, 0.5), *self.size)
        self.assertEqual(self.editor.waveform.points[0], moved)

    def test_pinch_started_away_from_point_does_not_capture_mid_gesture(self):
        self.editor.waveform.add_point(0.5)
        self.editor.drag_at_pinch((0.2, 0.5), *self.size)
        self.editor.drag_at_pinch((0.5, 0.5), *self.size)
        self.assertIsNone(self.editor.selected_id)

    def test_selected_point_survives_insertion_and_reset_clears_selection(self):
        point = self.editor.waveform.add_point(0.7)
        self.editor.drag_at_pinch((0.7, 0.5), *self.size)
        self.editor.add_at_pinch((0.3, 0.5), *self.size)
        self.editor.drag_at_pinch((0.7, 0.3), *self.size)
        self.assertEqual(self.editor.waveform.points[1].id, point.id)
        self.assertAlmostEqual(self.editor.waveform.points[1].y, 0.3)
        self.editor.reset()
        self.assertIsNone(self.editor.selected_id)
        self.editor.add_at_pinch((0.5, 0.5), *self.size)
        self.assertEqual(self.editor.waveform.points, ())


if __name__ == "__main__":
    unittest.main()
