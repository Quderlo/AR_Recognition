import socket
from threading import Thread
from search_for_faces import handle_client

# Код для создания серверного сокета и ожидания подключений
host = '127.0.0.1'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print(f"Сервер слушает на {host}:{port}")

while True:
    client_socket, client_address = server_socket.accept()

    # Создание и запуск потока для обработки клиента
    client_handler = Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
