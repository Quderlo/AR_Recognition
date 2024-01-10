# search_for_faces.py
import cv2
import pickle
import struct

import dlib

import settings


def detect_faces(frame):
    # Проверка на пустое изображение перед обработкой
    if frame is None or frame.size == 0:
        print("Ошибка: Изображение пустое.")
        return None, []

    # Преобразование кадра в оттенки серого (для улучшения производительности)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Обнаружение лиц на кадре
    faces = settings.face_detector(gray_frame)

    # Возвращение координат обнаруженных лиц
    return gray_frame, [(face.left(), face.top(), face.right(), face.bottom()) for face in faces]


def extract_faces(frame, faces):
    extracted_faces = []

    for i, (left, top, right, bottom) in enumerate(faces):
        face = frame[top:bottom, left:right]

        # Добавьте проверку на пустое изображение перед сохранением
        if not face.size == 0:
            extracted_faces.append(face)
        else:
            print(f"Изображение лица {i} пустое, не сохранено.")

    return extracted_faces


def encode_and_extract_face(frame, gray_frame, faces):
    encodings = []

    for i, (left, top, right, bottom) in enumerate(faces):
        face = frame[top:bottom, left:right]

        if not face.size == 0:
            landmarks = settings.shape_predictor(gray_frame, dlib.rectangle(left, top, right, bottom))
            encoding = settings.face_recognizer.compute_face_descriptor(image, landmarks)
        else:
            print(f"Изображение лица {i} пустое, не сохранено.")


def handle_client(client_socket):
    try:
        while True:
            # Принятие размера данных
            data_size = struct.unpack("Q", client_socket.recv(struct.calcsize("Q")))[0]

            # Получение данных
            data = b""
            while len(data) < data_size:
                packet = client_socket.recv(4 * 1024)  # 4 КБ чанки
                if not packet:
                    break
                data += packet

            # Десериализация изображения
            frame = pickle.loads(data)

            # Обнаружение лиц на изображении
            gray_frame, faces = detect_faces(frame)

            # Извлечение обрезанных лиц и сохранение их
            extracted_faces = extract_faces(frame, faces)

            encode_and_extract_face(frame, gray_frame, faces)

            # Сериализация обрезанных лиц и отправка клиенту
            extracted_faces_data = pickle.dumps(extracted_faces)
            client_socket.sendall(struct.pack("Q", len(extracted_faces_data)))
            client_socket.sendall(extracted_faces_data)

            print("Действие: Отправка ответа клиенту выполнена")

    except Exception as e:
        print(f"Ошибка при обработке изображения: {e}")

    finally:
        # Закрытие соединения с текущим клиентом
        client_socket.close()
