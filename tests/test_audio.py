import unittest

import numpy as np

from camara.audio import WavetableOscillator, build_wavetable
from camara.config import AUDIO_GAIN, FREQUENCY, SAMPLE_RATE, TABLE_SIZE
from camara.waveform import Waveform


def shaped_wave():
    wave = Waveform()
    point = wave.add_point(0.3)
    wave.move_point(point.id, 0.2)
    return wave


class AudioTests(unittest.TestCase):
    def test_flat_line_produces_exact_silence(self):
        table = build_wavetable(Waveform())
        self.assertFalse(np.any(table))
        oscillator = WavetableOscillator()
        oscillator.set_table(table)
        output = np.empty(SAMPLE_RATE, dtype=np.float32)
        oscillator.render(output)
        self.assertFalse(np.any(output))

    def test_table_is_finite_bounded_and_removes_dc_and_ultrasonic_harmonics(self):
        table = build_wavetable(shaped_wave())
        self.assertTrue(np.all(np.isfinite(table)))
        self.assertGreater(np.max(np.abs(table)), 0.1)
        self.assertLessEqual(np.max(np.abs(table)), 1)
        self.assertAlmostEqual(float(table.mean()), 0, places=7)
        spectrum = np.abs(np.fft.rfft(table)) / TABLE_SIZE
        last_harmonic = int((SAMPLE_RATE / 2 - 1) / FREQUENCY)
        self.assertLess(spectrum[last_harmonic + 1:].max(), 1e-7)

    def test_complete_curve_repeats_at_440_hz(self):
        oscillator = WavetableOscillator()
        oscillator.set_table(build_wavetable(shaped_wave()))
        oscillator.render(np.empty(SAMPLE_RATE, dtype=np.float32))  # Dejar acabar la transición.
        output = np.empty(SAMPLE_RATE, dtype=np.float32)
        oscillator.render(output)
        spectrum = np.abs(np.fft.rfft(output))
        frequencies = np.fft.rfftfreq(len(output), 1 / SAMPLE_RATE)
        self.assertEqual(frequencies[np.argmax(spectrum)], FREQUENCY)
        harmonic_bins = np.arange(int(FREQUENCY), int(SAMPLE_RATE / 2), int(FREQUENCY))
        self.assertGreater(np.sum(spectrum[harmonic_bins] ** 2) / np.sum(spectrum ** 2), 0.9999)
        self.assertLess(np.max(np.abs(output)), AUDIO_GAIN)

    def test_edit_changes_harmonic_balance_not_just_loudness(self):
        wave = shaped_wave()
        before = np.abs(np.fft.rfft(build_wavetable(wave)))[1:10]
        # Un valle cercano al pico añade armónicos claramente distinguibles.
        point = wave.add_point(0.4)
        wave.move_point(point.id, 0.85)
        after = np.abs(np.fft.rfft(build_wavetable(wave)))[1:10]
        before /= np.linalg.norm(before)
        after /= np.linalg.norm(after)
        self.assertGreater(np.linalg.norm(before - after), 0.1)

    def test_audio_remains_continuous_across_callback_sizes(self):
        table = build_wavetable(shaped_wave())
        whole = WavetableOscillator()
        chunked = WavetableOscillator()
        whole.set_table(table)
        chunked.set_table(table)
        expected = np.empty(10000, dtype=np.float32)
        actual = np.empty_like(expected)
        whole.render(expected)
        for start in range(0, len(actual), 113):
            chunked.render(actual[start:start + 113])
        np.testing.assert_allclose(actual, expected, atol=1e-7, rtol=1e-5)

    def test_changes_morph_smoothly_and_reset_returns_to_silence(self):
        oscillator = WavetableOscillator()
        oscillator.set_table(build_wavetable(shaped_wave()))
        output = np.empty(SAMPLE_RATE, dtype=np.float32)
        oscillator.render(output)
        last_sample = output[-1]
        oscillator.set_table(build_wavetable(Waveform()))
        oscillator.render(output)
        self.assertLess(abs(output[0] - last_sample), 0.01)
        self.assertLess(np.max(np.abs(output[-1000:])), 1e-7)


if __name__ == "__main__":
    unittest.main()
