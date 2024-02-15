import pickle
import socket
from datetime import datetime as dt
import cv2

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

        cv2.imwrite(f"{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg", image)

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



