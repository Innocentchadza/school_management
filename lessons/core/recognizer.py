import os
import cv2
import numpy as np
from django.conf import settings

FACE_SIZE = (200, 200)

_face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

_cached_recognizer = None
_cached_id_to_name = None


def _detect_and_crop(gray_image):
    faces = _face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return cv2.resize(gray_image[y:y + h, x:x + w], FACE_SIZE)


def _train():
    known_dir = settings.KNOWN_FACES_DIR
    samples, labels = [], []
    id_to_name = {}
    next_id = 0

    for person_name in sorted(os.listdir(known_dir)):
        person_dir = os.path.join(known_dir, person_name)
        if not os.path.isdir(person_dir):
            continue
        person_id = next_id
        id_to_name[person_id] = person_name
        next_id += 1

        for filename in os.listdir(person_dir):
            path = os.path.join(person_dir, filename)
            img = cv2.imread(path)
            if img is None:
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face = _detect_and_crop(gray)
            if face is not None:
                samples.append(face)
                labels.append(person_id)

    if not samples:
        raise RuntimeError(f"No usable training faces found in {known_dir}")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(samples, np.array(labels))
    return recognizer, id_to_name


def get_recognizer():
    global _cached_recognizer, _cached_id_to_name
    if _cached_recognizer is None:
        _cached_recognizer, _cached_id_to_name = _train()
    return _cached_recognizer, _cached_id_to_name


def reload_recognizer():
    global _cached_recognizer, _cached_id_to_name
    _cached_recognizer, _cached_id_to_name = _train()


def identify_face(bgr_image):
    recognizer, id_to_name = get_recognizer()
    gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    face = _detect_and_crop(gray)
    if face is None:
        return None, None
    label_id, confidence = recognizer.predict(face)
    return id_to_name[label_id], confidence
    
