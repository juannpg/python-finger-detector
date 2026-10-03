"""Carga y reproduce las cuatro muestras de batería."""

from pathlib import Path

import pygame.mixer


SOUND_DIR = Path(__file__).resolve().parent.parent / "assets" / "sounds"
SOUND_NAMES = ("kick", "snare", "hihat", "splash")


class SamplePlayer:
    def __init__(self) -> None:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=256)
        except pygame.error as exc:
            raise RuntimeError(f"No se pudo iniciar el audio: {exc}") from exc

        pygame.mixer.set_num_channels(16)
        try:
            self._sounds = {
                name: pygame.mixer.Sound(str(SOUND_DIR / f"{name}.wav"))
                for name in SOUND_NAMES
            }
        except (FileNotFoundError, pygame.error):
            pygame.mixer.quit()
            raise

    def play(self, name: str) -> None:
        self._sounds[name].play()

    def close(self) -> None:
        pygame.mixer.quit()

    def __enter__(self) -> "SamplePlayer":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
