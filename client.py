import pickle
import socket

# Локальный IP-адрес и порт сервера
import struct

import cv2
import numpy as np

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
    cv2.waitKey(3000)

    # Отправляем запрос на сервер о готовности принять данные
    client_socket.sendall(b"READY")

    # Ждем подтверждения от сервера
    response = client_socket.recv(1024)

    if response != b"READY":
        print("Ошибка: сервер не готов принять данные")
        continue

    if not result:
        print("Не удалось захватить изображение с веб-камеры.")
        continue
    else:
        print("Сериализация изображения")
        data = pickle.dumps(image)

        # Отправка размера данных перед отправкой самих данных
        client_socket.sendall(struct.pack("Q", len(data)))

        # Отправка данных
        client_socket.sendall(data)

    try:
        # Получаем размер данных от сервера
        data_size = struct.unpack("Q", client_socket.recv(struct.calcsize("Q")))[0]

        # Получаем данные от сервера
        data_from_server = b""
        while len(data_from_server) < data_size:
            packet = client_socket.recv(4 * 1024)  # Получаем данные пакетами по 4 КБ
            if not packet:
                break
            data_from_server += packet
    except struct.error as se:
        print(f"Ошибка при получении данных с сервера. {se}")
        data_from_server = []

    try:
        if data_from_server:
            # Десериализуем данные
            response_data = pickle.loads(data_from_server)

            # Проверяем, есть ли данные в response_data
            if response_data:
                for user in response_data:
                    # Если данные есть, выводим их
                    print("Данные из базы данных:")
                    print(f"Фамилия: {user[0]}")
                    print(f"Имя: {user[1]}")
                    print(f"Отчество: {user[2]}")
                    print(f"Университет: {user[3]}")

                    # Преобразование изображения из байтовой строки в массив numpy
                    image_bytes = user[4]
                    image_array = np.frombuffer(image_bytes, dtype=np.uint8)

                    # Декодирование изображения
                    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                    # Отображение изображения
                    # cv2.imshow("Image", image)
                    # cv2.waitKey(0)
                    # cv2.destroyAllWindows()
            else:
                print("Нет данных в response_data")
        else:
            print("Нет данных в data_from_server")
    except Exception as e:
        print(f"Ошибка при десериализации данных. {e}")

cap.release()
client_socket.close()
