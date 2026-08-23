import argparse
import os
import cv2
import numpy as np

FACE_SIZE = (200, 200)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def detect_and_crop_face(gray_image):
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face = gray_image[y:y + h, x:x + w]
    return cv2.resize(face, FACE_SIZE)

def train_recognizer(known_dir):
    samples = []
    labels = []
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
            face = detect_and_crop_face(gray)
            if face is None:
                print(f" [skip] no face found in {path}")
                continue

            samples.append(face)
            labels.append(person_id)
            print(f" [loaded] {person_name} <- {filename}")

    if not samples:
        raise RuntimeError("No usable training faces found — check your known_faces folder.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(samples, np.array(labels))
    return recognizer, id_to_name

def recognize_in_video(video_source, recognizer, id_to_name,
                        confidence_threshold=70, output_path=None):
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video source: {video_source}")

    writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    print("Starting camera... Press 'q' to quit")
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        for (x, y, w, h) in faces:
            face_crop = cv2.resize(gray[y:y + h, x:x + w], FACE_SIZE)
            label_id, confidence = recognizer.predict(face_crop)

            if confidence <= confidence_threshold:
                name = f"{id_to_name[label_id]} ({confidence:.0f})"
                color = (0, 255, 0)
            else:
                name = f"Unknown ({confidence:.0f})"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.rectangle(frame, (x, y + h - 22), (x + w, y + h), color, cv2.FILLED)
            cv2.putText(frame, name, (x + 6, y + h - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        cv2.imshow('Webcam face recognition LBPH — press q to quit', frame)
        if writer:
            writer.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recognize known people from webcam using LBPH.")
    parser.add_argument("--known", required=True, help="Path to known_faces folder")
    parser.add_argument("--video", default="0", help="Path to video file, or '0' for webcam. Default=0")
    parser.add_argument("--threshold", type=float, default=70, help="Max LBPH distance to count as a match (lower = stricter)")
    parser.add_argument("--output", default=None, help="Optional path to save annotated video, e.g. out.mp4")
    args = parser.parse_args()

    print(f"Training recognizer from '{args.known}'...")
    recognizer, id_to_name = train_recognizer(args.known)
    print(f"Trained on {len(id_to_name)} people: {list(id_to_name.values())}\n")

    video_source = 0 if args.video == "0" else args.video
    recognize_in_video(video_source, recognizer, id_to_name,
                        confidence_threshold=args.threshold, output_path=args.output)