"""Conecta la webcam, el detector y el dibujo."""

from time import monotonic
from collections.abc import Callable

import cv2
import numpy as np

from camara.audio import SamplePlayer
from camara.config import BPM, CAMERA_INDEX, MIRROR_IMAGE, WINDOW_TITLE
from camara.sequencer import DrumMachine
from camara.tracker import Hand, HandTracker


def run(process_frame: Callable[[np.ndarray, list[Hand], DrumMachine], None]) -> None:
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError("No se pudo abrir la webcam. Comprueba los permisos de cámara.")

    try:
        with SamplePlayer() as audio, HandTracker() as tracker:
            machine = DrumMachine(audio.play, BPM)
            while True:
                ok, frame = camera.read()
                if not ok:
                    raise RuntimeError("Se perdió la imagen de la webcam.")

                if MIRROR_IMAGE:
                    frame = cv2.flip(frame, 1)

                hands = tracker.detect(frame)
                process_frame(frame, hands, machine)
                machine.tick(monotonic())

                cv2.imshow(WINDOW_TITLE, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        camera.release()
        cv2.destroyAllWindows()
