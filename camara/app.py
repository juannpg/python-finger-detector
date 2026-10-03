"""Bucle de cámara, audio continuo y cierre de recursos."""

from collections.abc import Callable

import cv2
import numpy as np

from camara.audio import WaveformPlayer
from camara.config import CAMERA_INDEX, MIRROR_IMAGE, WINDOW_TITLE
from camara.tracker import Hand, HandTracker
from camara.waveform import WaveformEditor


def run(process_frame: Callable[[np.ndarray, list[Hand], WaveformEditor], None]) -> None:
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError("No se pudo abrir la webcam. Comprueba los permisos de cámara.")

    try:
        with HandTracker() as tracker, WaveformPlayer() as audio:
            editor = WaveformEditor()
            while True:
                ok, frame = camera.read()
                if not ok:
                    raise RuntimeError("Se perdió la imagen de la webcam.")
                if MIRROR_IMAGE:
                    frame = cv2.flip(frame, 1)
                process_frame(frame, tracker.detect(frame), editor)
                audio.update(editor.waveform)
                cv2.imshow(WINDOW_TITLE, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or cv2.getWindowProperty(WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1:
                    break
                if key == ord("r"):
                    editor.reset()
                    audio.update(editor.waveform)
    finally:
        camera.release()
        cv2.destroyAllWindows()
