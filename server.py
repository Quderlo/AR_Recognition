import pickle
import socket
from datetime import datetime as dt
import cv2
import numpy as np
from get_compare_data import get_users_data
import settings

from close_socket import close_server_soket
import struct

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Локальный IP-адрес и порт
host = '127.0.0.1'  # Локальный IP-адрес
port = 12345  # Произвольный порт
data = b""
running = True

# Привязываем сокет к адресу и порту
server_socket.bind((host, port))

# Ждем клиентских подключений
server_socket.listen(5)

print("Ждем подключений...")

# Принимаем подключение
client_socket, addr = server_socket.accept()

print("Подключился клиент с IP:", addr[0])

while running:
    try:
        request = client_socket.recv(1024)
        if request != b"READY":
            print("Ошибка: неверный запрос от клиента")
            continue

        # Отправляем подтверждение клиенту
        client_socket.sendall(b"READY")

        data_size = struct.unpack("Q", client_socket.recv(struct.calcsize("Q")))[0]

        try:
            # Получение данных
            data = b""
            while len(data) < data_size:
                packet = client_socket.recv(4 * 1024)  # 4 КБ чанки
                if not packet:
                    break
                data += packet

        except struct.error as se:
            print(f"Error: {se}")
        except Exception as e:
            print(f"Error: {e}")

        image = pickle.loads(data)
        faces = settings.face_detector(image, 3)

        face_descriptors = []

        for i, face in enumerate(faces):
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

            cropped_face = image[y1:y2, x1:x2]

            # cv2.imwrite(f"photo/{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}_face_{i}.jpg", cropped_face)

            landmarks = settings.shape_predictor(image, face)
            face_descriptors.append(np.array(settings.face_recognizer.compute_face_descriptor(image, landmarks)))

        # Получение данных о пользователях
        user_data = get_users_data(face_descriptors)

        # Сериализация данных
        serialized_data = pickle.dumps(user_data)

        # Отправка размера данных перед отправкой самих данных
        client_socket.sendall(struct.pack("Q", len(serialized_data)))

        # Отправка данных на клиент
        try:
            # Отправляем данные на клиент
            client_socket.sendall(serialized_data)
        except Exception as e:
            print(f"Error: {e}")

    except OSError as oe:
        print(f"Error: {oe}")
        running = close_server_soket(server_socket, client_socket)
    except Exception as e:
        print(f"Error: {e}")
        running = close_server_soket(server_socket, client_socket)
