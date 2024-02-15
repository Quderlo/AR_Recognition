import pickle
import socket

# Локальный IP-адрес и порт сервера
import struct
import time

import cv2

server_host = '127.0.0.1'  # Локальный IP-адрес сервера
server_port = 12345  # Порт сервера
running = True
data = None

# Создаем сокет клиента
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Подключаемся к серверу
client_socket.connect((server_host, server_port))

# Получаем локальный IP-адрес и порт клиента
local_ip = client_socket.getsockname()[0]
local_port = client_socket.getsockname()[1]

print(f"Подключились к серверу {server_host} через {local_ip}:{local_port}")

cap = cv2.VideoCapture(0)

while running:
    # Проверяем, успешно ли произошел захват изображения
    result, image = cap.read()
    cv2.waitKey(10)

    if not result:
        print("Не удалось захватить изображение с веб-камеры.")
    else:
        print("Сериализация изображения")
        data = pickle.dumps(image)

        # Отправка размера данных перед отправкой самих данных
        client_socket.sendall(struct.pack("Q", len(data)))

        # Отправка данных
        client_socket.sendall(data)

        response = client_socket.recv(1024)
        print(f"Ответ сервера {response}")

        if response != b"200":
            running = False


cap.release()
client_socket.close()
