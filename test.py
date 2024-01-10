import cv2
import dlib
import settings
import time
import multiprocessing


def encode_face(args):
    frame, landmarks = args
    return settings.face_recognizer.compute_face_descriptor(frame, landmarks, num_jitters=0)


cap = cv2.VideoCapture(0, cv2.CAP_VFW)

while True:
    start_time = time.time()

    result, frame = cap.read()

    if result:
        cv2.imshow("Standard frame", frame)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Gray frame", gray_frame)

        faces = settings.face_detector(gray_frame)

        faces = [(face.left(), face.top(), face.right(), face.bottom()) for face in faces]

        print(f"faces rect positions = {faces}")

        landmarks = []

        for i, (left, top, right, bottom) in enumerate(faces):
            face = frame[top:bottom, left:right]

            cv2.imshow("Cutted face", face)

            landmarks.append(settings.shape_predictor(gray_frame, dlib.rectangle(left, top, right, bottom)))
            print(f"Is_landmarks {landmarks}")

        with multiprocessing.Pool(processes=len(landmarks)) as pool:
            encodings = pool.map(encode_face, landmarks)

        for i, encoding in enumerate(encodings):
            print(f"Face {i + 1} encoding: {encoding}")

        execution_time = time.time() - start_time
        print(f"Total execution time: {execution_time:.4f} seconds")

        cv2.waitKey(0)
