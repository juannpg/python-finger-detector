import unittest

from camara.sequencer import DrumMachine


class DrumMachineTests(unittest.TestCase):
    def test_all_rows_start_at_zero_and_keep_a_fixed_order(self):
        machine = DrumMachine(lambda _: None, start_at=0)
        self.assertEqual(
            machine.patterns,
            {
                "kick": (0, 0, 0, 0),
                "snare": (0, 0, 0, 0),
                "hihat": (0, 0, 0, 0),
                "splash": (0, 0, 0, 0),
            },
        )
        machine.confirm("kick", (1, 0, 1, 1))
        machine.confirm("kick", (0, 0, 0, 0))  # Mismo contacto: no reescribe.
        self.assertEqual(machine.patterns["kick"], (1, 0, 1, 1))

        for _ in range(3):
            machine.confirm(None, None)
        machine.confirm("snare", (0, 1, 0, 1))
        for _ in range(3):
            machine.confirm(None, None)
        machine.confirm("kick", (1, 1, 0, 0))

        self.assertEqual(list(machine.patterns), ["kick", "snare", "hihat", "splash"])
        self.assertEqual(machine.patterns["kick"], (1, 1, 0, 0))

    def test_four_beat_loop_at_80_bpm(self):
        played = []
        machine = DrumMachine(played.append, bpm=80, start_at=10.0)
        machine.confirm("kick", (1, 0, 1, 0))
        for _ in range(3):
            machine.confirm(None, None)
        machine.confirm("snare", (0, 1, 0, 1))

        for beat in range(8):
            machine.tick(10.0 + beat * 0.75)
        self.assertEqual(played, ["kick", "snare", "kick", "snare"] * 2)

    def test_skips_missed_beats_without_burst(self):
        played = []
        machine = DrumMachine(played.append, bpm=80, start_at=0)
        machine.confirm("hihat", (1, 1, 1, 1))
        machine.tick(0)
        machine.tick(3.75)  # La cámara se retrasó cinco tiempos.
        self.assertEqual(played, ["hihat", "hihat"])

    def test_eighths_alternate_halves_and_quarters_reset_the_row(self):
        machine = DrumMachine(lambda _: None, start_at=0)

        machine.toggle_mode()
        self.assertEqual(machine.mode, "eighth")
        for _ in range(3):
            machine.confirm(None, None)
        machine.confirm("kick", (1, 0, 1, 0))
        self.assertEqual(machine.patterns["kick"], (1, 0, 1, 0, 0, 0, 0, 0))
        self.assertEqual(machine.patterns["snare"], (0, 0, 0, 0))

        for _ in range(3):
            machine.confirm(None, None)
        machine.confirm("kick", (0, 1, 0, 1))
        self.assertEqual(machine.patterns["kick"], (1, 0, 1, 0, 0, 1, 0, 1))

        for _ in range(3):
            machine.confirm(None, None)
        machine.confirm("kick", (1, 1, 1, 1))
        self.assertEqual(machine.patterns["kick"], (1, 1, 1, 1, 0, 1, 0, 1))

        for _ in range(3):
            machine.confirm(None, None)
        machine.toggle_mode()
        self.assertEqual(machine.mode, "quarter")
        self.assertEqual(machine.patterns["kick"], (1, 1, 1, 1, 0, 1, 0, 1))
        for _ in range(3):
            machine.confirm(None, None)
        machine.confirm("kick", (0, 1, 0, 1))
        self.assertEqual(machine.patterns["kick"], (0, 1, 0, 1))

        for _ in range(3):
            machine.confirm(None, None)
        machine.toggle_mode()
        for _ in range(3):
            machine.confirm(None, None)
        machine.confirm("kick", (0, 0, 1, 1))
        self.assertEqual(machine.patterns["kick"], (0, 0, 1, 1, 0, 0, 0, 0))

    def test_eighths_play_between_quarter_beats(self):
        played = []
        machine = DrumMachine(played.append, bpm=80, start_at=0)
        machine.confirm("kick", (1, 1, 1, 1))
        for _ in range(3):
            machine.confirm(None, None)
        machine.toggle_mode()
        for _ in range(3):
            machine.confirm(None, None)
        machine.confirm("snare", (0, 1, 0, 1))

        events = []
        for step in range(8):
            before = len(played)
            machine.tick(step * 0.375)
            events.append(played[before:])
        self.assertEqual(
            events,
            [["kick"], ["snare"], ["kick"], ["snare"], ["kick"], [], ["kick"], []],
        )


if __name__ == "__main__":
    unittest.main()
