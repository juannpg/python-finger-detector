import unittest

import numpy as np

from camara.config import ADD_HAND, DRAG_HAND, INDEX_TIP, THUMB_TIP, WHITE
from camara.detectors import pinch_position
from camara.tracker import Hand, Point
from camara.waveform import WaveformEditor
from main import process_frame


def hand_at(side, x, y, gap=0.01):
    points = [Point(x, y)] * 21
    points[0] = Point(x, y + 0.25)
    points[9] = Point(x, y)
    points[THUMB_TIP] = Point(x - gap / 2, y)
    points[INDEX_TIP] = Point(x + gap / 2, y)
    return Hand(side, tuple(points))


class InteractionTests(unittest.TestCase):
    def setUp(self):
        self.frame = np.zeros((601, 1001, 3), dtype=np.uint8)
        self.editor = WaveformEditor()

    def test_physical_left_adds_and_physical_right_drags(self):
        process_frame(self.frame, [hand_at(ADD_HAND, 0.4, 0.5)], self.editor)
        self.assertEqual(len(self.editor.waveform.points), 1)
        point = self.editor.waveform.points[0]
        process_frame(self.frame, [hand_at(DRAG_HAND, point.x, point.y)], self.editor)
        self.assertEqual(self.editor.selected_id, point.id)
        process_frame(self.frame, [hand_at(DRAG_HAND, 0.6, 0.3)], self.editor)
        self.assertAlmostEqual(self.editor.waveform.points[0].y, 0.3)
        self.assertEqual(self.editor.waveform.points[0].x, point.x)
        process_frame(self.frame, [], self.editor)
        self.assertIsNone(self.editor.selected_id)
        self.assertFalse(self.editor.left_pinched)
        self.assertFalse(self.editor.right_pinched)

    def test_right_hand_cannot_create_points(self):
        process_frame(self.frame, [hand_at(DRAG_HAND, 0.5, 0.5)], self.editor)
        self.assertEqual(self.editor.waveform.points, ())

    def test_thumb_and_index_have_white_markers_on_both_hands(self):
        hands = [hand_at(ADD_HAND, 0.25, 0.6, 0.1), hand_at(DRAG_HAND, 0.75, 0.6, 0.1)]
        process_frame(self.frame, hands, self.editor)
        for hand in hands:
            for tip in (THUMB_TIP, INDEX_TIP):
                point = hand.points[tip]
                pixel = self.frame[round(point.y * 600), round(point.x * 1000)]
                np.testing.assert_array_equal(pixel, WHITE)

    def test_pinch_hysteresis_avoids_retriggering_with_small_gap_changes(self):
        hand = hand_at(ADD_HAND, 0.5, 0.5, gap=0.036)
        self.assertIsNone(pinch_position(self.frame, hand, False))
        self.assertIsNotNone(pinch_position(self.frame, hand, True))
        self.assertIsNone(pinch_position(self.frame, hand_at(ADD_HAND, 0.5, 0.5, gap=0.06), True))
        self.assertIsNone(pinch_position(self.frame, None, True))


if __name__ == "__main__":
    unittest.main()
