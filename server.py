import pickle
import socket
from datetime import datetime as dt
import cv2
import numpy as np

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
        face_encoding = np.array
        print(face_encoding)

        for i, face in enumerate(faces):
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

            cropped_face = image[y1:y2, x1:x2]

            cv2.imwrite(f"photo/{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}_face_{i}.jpg", cropped_face)

            landmarks = settings.shape_predictor(image, face)
            face_encoding = np.array(settings.face_recognizer.compute_face_descriptor(image, landmarks))
            print("after", face_encoding)

        # cv2.imwrite(f"photo/{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg", image)

        try:
            # Отправляем клиенту код 200
            client_socket.sendall(b"200")
        except Exception as e:
            print(f"Error: {e}")

    except OSError as oe:
        print(f"Error: {oe}")
        running = close_server_soket(server_socket, client_socket)
    except Exception as e:
        print(f"Error: {e}")
        running = close_server_soket(server_socket, client_socket)
