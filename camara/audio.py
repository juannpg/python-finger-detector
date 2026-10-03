"""Síntesis continua: todo el ancho de la curva es un período a 440 Hz."""

from __future__ import annotations

from time import sleep

import numpy as np
import sounddevice as sd

from camara.config import (
    AUDIO_BLOCK_SIZE, AUDIO_GAIN, AUDIO_MORPH_SECONDS,
    FREQUENCY, SAMPLE_RATE, TABLE_SIZE, WAVE_CENTER,
)
from camara.waveform import Waveform


def build_wavetable(waveform: Waveform) -> np.ndarray:
    """Convierte un ciclo dibujado en muestras, sin DC ni armónicos sobre Nyquist."""
    phase = np.arange(TABLE_SIZE) / TABLE_SIZE
    samples = 2 * (WAVE_CENTER - waveform.sample(phase))
    spectrum = np.fft.rfft(samples)
    spectrum[0] = 0  # Desplazar la curva verticalmente no debe enviar DC al altavoz.
    max_harmonic = int((SAMPLE_RATE / 2 - 1) / FREQUENCY)
    spectrum[max_harmonic + 1:] = 0
    table = np.fft.irfft(spectrum, n=TABLE_SIZE)
    table /= max(1.0, float(np.max(np.abs(table))))
    return table.astype(np.float32)


class WavetableOscillator:
    """Fase continua y transición suave entre formas, con buffers reutilizables."""

    def __init__(self) -> None:
        self._target = np.zeros(TABLE_SIZE, dtype=np.float32)
        self._current = self._target.copy()
        self._table_delta = self._target.copy()
        self._phase = 0.0
        self._step = FREQUENCY * TABLE_SIZE / SAMPLE_RATE
        self._offsets = np.arange(AUDIO_BLOCK_SIZE, dtype=np.float64) * self._step
        self._positions = np.empty(AUDIO_BLOCK_SIZE, dtype=np.float64)
        self._indices = np.empty(AUDIO_BLOCK_SIZE, dtype=np.intp)
        self._next_indices = np.empty_like(self._indices)
        self._fraction = np.empty(AUDIO_BLOCK_SIZE, dtype=np.float32)
        self._interpolation_delta = np.empty_like(self._fraction)
        self._new_samples = np.empty_like(self._fraction)
        self._weights = (1 - np.exp(
            -np.arange(1, AUDIO_BLOCK_SIZE + 1) / (SAMPLE_RATE * AUDIO_MORPH_SECONDS)
        )).astype(np.float32)

    def set_table(self, table: np.ndarray) -> None:
        # Se prepara en el hilo de cámara y se publica una referencia inmutable.
        if table.shape != (TABLE_SIZE,) or not np.all(np.isfinite(table)):
            raise ValueError("La tabla de onda debe contener muestras finitas de un ciclo.")
        target = np.array(table, dtype=np.float32, copy=True)
        target.setflags(write=False)
        self._target = target

    def _lookup(self, table: np.ndarray, output: np.ndarray, count: int) -> None:
        delta = self._interpolation_delta[:count]
        np.take(table, self._indices[:count], out=output)
        np.take(table, self._next_indices[:count], out=delta)
        np.subtract(delta, output, out=delta)
        np.multiply(delta, self._fraction[:count], out=delta)
        np.add(output, delta, out=output)

    def render(self, output: np.ndarray) -> None:
        """Rellena un buffer mono sin FFT, interpolación de splines ni I/O."""
        target = self._target
        for start in range(0, len(output), AUDIO_BLOCK_SIZE):
            block = output[start:start + AUDIO_BLOCK_SIZE]
            count = len(block)
            positions = self._positions[:count]
            np.add(self._offsets[:count], self._phase, out=positions)
            np.remainder(positions, TABLE_SIZE, out=positions)
            np.copyto(self._indices[:count], positions, casting="unsafe")
            np.subtract(positions, self._indices[:count], out=self._fraction[:count])
            np.add(self._indices[:count], 1, out=self._next_indices[:count])
            np.remainder(self._next_indices[:count], TABLE_SIZE, out=self._next_indices[:count])

            self._lookup(self._current, block, count)
            new = self._new_samples[:count]
            self._lookup(target, new, count)
            np.subtract(new, block, out=new)
            np.multiply(new, self._weights[:count], out=new)
            np.add(block, new, out=block)
            np.multiply(block, AUDIO_GAIN, out=block)

            np.subtract(target, self._current, out=self._table_delta)
            np.multiply(self._table_delta, self._weights[count - 1], out=self._table_delta)
            np.add(self._current, self._table_delta, out=self._current)
            self._phase = (self._phase + count * self._step) % TABLE_SIZE


class WaveformPlayer:
    def __init__(self) -> None:
        self.oscillator = WavetableOscillator()
        self._revision = -1
        self._stream: sd.OutputStream | None = None
        self._error: Exception | None = None

    def update(self, waveform: Waveform) -> None:
        self.check()
        if waveform.revision != self._revision:
            self.oscillator.set_table(build_wavetable(waveform))
            self._revision = waveform.revision

    def _callback(self, outdata, frames, time_info, status) -> None:
        try:
            self.oscillator.render(outdata[:, 0])
        except Exception as exc:
            outdata.fill(0)
            self._error = exc

    def check(self) -> None:
        if self._error is not None:
            raise RuntimeError("Se interrumpió la síntesis de audio.") from self._error
        if self._stream is not None and not self._stream.active:
            raise RuntimeError("Se detuvo la salida de audio.")

    def __enter__(self) -> "WaveformPlayer":
        try:
            self._stream = sd.OutputStream(
                samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                blocksize=AUDIO_BLOCK_SIZE, latency="low", callback=self._callback,
            )
            self._stream.start()
        except sd.PortAudioError as exc:
            if self._stream is not None:
                self._stream.close()
            raise RuntimeError("No se pudo abrir la salida de audio. Comprueba el dispositivo de sonido.") from exc
        return self

    def close(self) -> None:
        if self._stream is not None:
            try:
                self.oscillator.set_table(np.zeros(TABLE_SIZE, dtype=np.float32))
                if self._stream.active:
                    sleep(AUDIO_MORPH_SECONDS * 3)
                    self._stream.stop()
            finally:
                self._stream.close()
                self._stream = None

    def __exit__(self, *_: object) -> None:
        self.close()
