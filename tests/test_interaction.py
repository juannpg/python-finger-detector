import unittest
from math import cos, radians, sin

import numpy as np

from camara.config import CONTROL_HAND, PATTERN_HAND
from camara.sequencer import DrumMachine
from camara.tracker import Hand, Point
from main import CONTROL_TARGETS, process_frame


def pattern_hand(middle_raised: bool) -> Hand:
    points = [Point(0.5, 0.9) for _ in range(21)]
    points[0] = Point(0.5, 0.95)
    for joints, x in zip(
        ((5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 16), (17, 18, 19, 20)),
        (0.3, 0.45, 0.65, 0.85),
    ):
        for index, y in zip(joints, (0.7, 0.55, 0.4, 0.25)):
            points[index] = Point(x, y)
    if not middle_raised:
        points[12] = Point(0.45, 0.65)
    return Hand(PATTERN_HAND, tuple(points))


def control_hand(target: str = "kick") -> Hand:
    points = [Point(0.8, 0.8) for _ in range(21)]
    points[0] = Point(0.1, 0.9)
    points[9] = Point(0.1, 0.5)
    points[4] = Point(0.2, 0.2)   # Pulgar de confirmar.
    landmarks = {"kick": 8, "mode": 17}
    points[landmarks[target]] = Point(0.21, 0.2)
    return Hand(CONTROL_HAND, tuple(points))


def slider_hand(angle: float, touching: bool) -> Hand:
    points = list(pattern_hand(True).points)
    wrist_x, wrist_y = points[0].x * 640, points[0].y * 400
    turn = radians(angle)
    for index, point in enumerate(points):
        x, y = point.x * 640 - wrist_x, point.y * 400 - wrist_y
        points[index] = Point(
            (wrist_x + x * cos(turn) - y * sin(turn)) / 640,
            (wrist_y + x * sin(turn) + y * cos(turn)) / 400,
        )
    points[4] = Point(points[17].x, points[17].y) if touching else Point(0.1, 0.9)
    return Hand(PATTERN_HAND, tuple(points))


class InteractionTests(unittest.TestCase):
    def test_only_pinky_base_is_a_mode_target(self):
        self.assertEqual(
            CONTROL_TARGETS,
            (("kick", 8), ("snare", 12), ("hihat", 16), ("splash", 20), ("mode", 17)),
        )

    def test_contact_captures_four_left_fingers_and_can_overwrite(self):
        frame = np.zeros((400, 640, 3), dtype=np.uint8)
        machine = DrumMachine(lambda _: None, start_at=0)
        right = control_hand()

        process_frame(frame.copy(), [pattern_hand(False), right], machine)
        self.assertEqual(machine.patterns["kick"], (1, 1, 0, 1))

        process_frame(frame.copy(), [pattern_hand(True), right], machine)
        self.assertEqual(machine.patterns["kick"], (1, 1, 0, 1))

        for _ in range(3):
            process_frame(frame.copy(), [pattern_hand(True)], machine)
        process_frame(frame.copy(), [pattern_hand(True), right], machine)
        self.assertEqual(machine.patterns["kick"], (1, 1, 1, 1))

    def test_mode_switch_changes_how_the_same_instrument_dot_records(self):
        frame = np.zeros((400, 640, 3), dtype=np.uint8)
        machine = DrumMachine(lambda _: None, start_at=0)

        process_frame(frame.copy(), [pattern_hand(False), control_hand("mode")], machine)
        self.assertEqual(machine.mode, "eighth")
        process_frame(frame.copy(), [pattern_hand(False), control_hand("mode")], machine)
        self.assertEqual(machine.mode, "eighth")
        for _ in range(3):
            process_frame(frame.copy(), [pattern_hand(False)], machine)

        process_frame(frame.copy(), [pattern_hand(False), control_hand()], machine)
        self.assertEqual(machine.patterns["kick"], (1, 1, 0, 1, 0, 0, 0, 0))

        for _ in range(3):
            process_frame(frame.copy(), [pattern_hand(True)], machine)
        process_frame(frame.copy(), [pattern_hand(True), control_hand()], machine)
        self.assertEqual(machine.patterns["kick"], (1, 1, 0, 1, 1, 1, 1, 1))

        # Mover el pulgar al interruptor sin separarlo no cambia el modo.
        process_frame(frame.copy(), [pattern_hand(False), control_hand("mode")], machine)
        self.assertEqual(machine.mode, "eighth")
        for _ in range(3):
            process_frame(frame.copy(), [pattern_hand(False)], machine)
        process_frame(frame.copy(), [pattern_hand(False), control_hand("mode")], machine)
        self.assertEqual(machine.mode, "quarter")
        self.assertEqual(machine.patterns["kick"], (1, 1, 0, 1, 1, 1, 1, 1))

        # Confirmar la punta en negras vuelve a cuatro notas.
        process_frame(frame.copy(), [pattern_hand(False), control_hand()], machine)
        self.assertEqual(machine.patterns["kick"], (1, 1, 0, 1, 1, 1, 1, 1))
        for _ in range(3):
            process_frame(frame.copy(), [pattern_hand(False)], machine)
        process_frame(frame.copy(), [pattern_hand(False), control_hand()], machine)
        self.assertEqual(machine.patterns["kick"], (1, 1, 0, 1))

    def test_white_hand_switch_controls_tempo_from_rotation(self):
        frame = np.zeros((400, 640, 3), dtype=np.uint8)
        machine = DrumMachine(lambda _: None, start_at=0)

        process_frame(frame.copy(), [slider_hand(0.0, True)], machine)
        self.assertTrue(machine.slider_active)
        self.assertEqual(machine.bpm, 80)
        self.assertEqual(machine.mode, "quarter")
        process_frame(frame.copy(), [slider_hand(0.0, True)], machine)
        self.assertTrue(machine.slider_active)

        for _ in range(12):
            process_frame(frame.copy(), [slider_hand(20, True)], machine)
        self.assertGreater(machine.bpm, 80)

        process_frame(frame.copy(), [slider_hand(20, False)], machine)
        self.assertFalse(machine.slider_active)
        stopped_bpm = machine.bpm
        for _ in range(20):
            process_frame(frame.copy(), [slider_hand(-20, False)], machine)
        self.assertEqual(machine.bpm, stopped_bpm)

        process_frame(frame.copy(), [slider_hand(-20, True)], machine)
        self.assertTrue(machine.slider_active)
        self.assertEqual(machine.bpm, stopped_bpm)
        for _ in range(12):
            process_frame(frame.copy(), [slider_hand(-40, True)], machine)
        self.assertLess(machine.bpm, stopped_bpm)
        process_frame(frame.copy(), [], machine)
        self.assertFalse(machine.slider_active)

    def test_slider_ignores_individual_finger_bending(self):
        frame = np.zeros((400, 640, 3), dtype=np.uint8)
        machine = DrumMachine(lambda _: None, start_at=0)
        process_frame(frame.copy(), [slider_hand(0.0, True)], machine)

        hand = slider_hand(0.0, True)
        points = list(hand.points)
        points[8] = Point(0.4, 0.65)
        for _ in range(5):
            process_frame(frame.copy(), [Hand(PATTERN_HAND, tuple(points))], machine)
        self.assertEqual(machine.bpm, 80)

    def test_slider_switch_uses_a_slightly_larger_touch_radius(self):
        frame = np.zeros((400, 640, 3), dtype=np.uint8)
        machine = DrumMachine(lambda _: None, start_at=0)
        hand = slider_hand(0.0, False)
        points = list(hand.points)
        points[4] = Point(points[17].x + 23 / 640, points[17].y)

        process_frame(frame.copy(), [Hand(PATTERN_HAND, tuple(points))], machine)
        self.assertTrue(machine.slider_active)


if __name__ == "__main__":
    unittest.main()
