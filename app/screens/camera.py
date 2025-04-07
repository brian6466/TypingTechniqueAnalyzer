import cv2
import numpy as np

for index in range(5):
    for backend in [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_MSMF]:
        print(f"\nTrying index {index} with backend {backend}")
        cap = cv2.VideoCapture(index, backend)
        if not cap.isOpened():
            print("Camera failed to open")
            continue

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            print("Frame is None or read failed")
            continue

        if not isinstance(frame, np.ndarray):
            print("Frame is not a valid NumPy array")
        else:
            print("✅ Valid frame captured!")
