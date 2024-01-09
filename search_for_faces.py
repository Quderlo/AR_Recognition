# search_for_faces.py
import cv2
import dlib
import pickle
import struct
from settings import SHAPE_PREDICTOR_PATH

# Загрузка предобученной модели dlib для обнаружения лиц
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(SHAPE_PREDICTOR_PATH)


def detect_faces(frame):
    # Преобразование кадра в оттенки серого (для улучшения производительности)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Обнаружение лиц на кадре
    faces = face_detector(gray_frame)

    # Возвращение координат обнаруженных лиц
    return [(face.left(), face.top(), face.right(), face.bottom()) for face in faces]


def extract_faces(frame, faces):
    extracted_faces = []
    for i, (left, top, right, bottom) in enumerate(faces):
        face = frame[top:bottom, left:right]
        extracted_faces.append(face)
        cv2.imwrite(f"serverImage/extracted_face_{i}.jpg", face)

    return extracted_faces


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
            faces = detect_faces(frame)

            # Отображение обнаруженных лиц на кадре (для проверки)
            for face in faces:
                cv2.rectangle(frame, (face[0], face[1]), (face[2], face[3]), (0, 255, 0), 2)

            # Извлечение обрезанных лиц и сохранение их
            extracted_faces = extract_faces(frame, faces)

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