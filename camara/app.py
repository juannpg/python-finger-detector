"""Conecta la webcam, el detector y el dibujo."""

from collections.abc import Callable

import cv2
import numpy as np

from camara.config import CAMERA_INDEX, MIRROR_IMAGE, WINDOW_TITLE
from camara.tracker import Hand, HandTracker


def run(process_frame: Callable[[np.ndarray, list[Hand], np.ndarray], None]) -> None:
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError("No se pudo abrir la webcam. Comprueba los permisos de cámara.")

    permanent_canvas = None
    try:
        with HandTracker() as tracker:
            while True:
                ok, frame = camera.read()
                if not ok:
                    raise RuntimeError("Se perdió la imagen de la webcam.")

                if MIRROR_IMAGE:
                    frame = cv2.flip(frame, 1)

                if permanent_canvas is None or permanent_canvas.shape != frame.shape:
                    permanent_canvas = np.zeros_like(frame)

                hands = tracker.detect(frame)
                process_frame(frame, hands, permanent_canvas)
                cv2.add(frame, permanent_canvas, dst=frame)

                cv2.imshow(WINDOW_TITLE, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        camera.release()
        cv2.destroyAllWindows()
