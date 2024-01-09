import socket
import cv2
import pickle
import struct

host = '127.0.0.1'
port = 12345

try:
    # Создание нового клиентского сокета
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # Захват изображения с камеры с помощью OpenCV
    cap = cv2.VideoCapture(0)

    while True:
        # Чтение кадра
        ret, frame = cap.read()

        # Сериализация изображения в байты
        data = pickle.dumps(frame)

        # Отправка размера данных перед отправкой самих данных
        sock.sendall(struct.pack("Q", len(data)))

        # Отправка данных
        sock.sendall(data)

        # Получение размера ответа от сервера
        response_size = struct.unpack("Q", sock.recv(struct.calcsize("Q")))[0]

        # Получение ответа от сервера
        response_data = b""
        while len(response_data) < response_size:
            packet = sock.recv(4 * 1024)  # 4 КБ чанки
            if not packet:
                break
            response_data += packet

        extracted_faces = pickle.loads(response_data)

        # Отображение изображений с обрезанными лицами
        for i, face in enumerate(extracted_faces):
            cv2.imshow(f"Face {i}", face)

        # Небольшая пауза между кадрами
        cv2.waitKey(10)

except KeyboardInterrupt:
    print("Клиент завершил работу.")

except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    # Закрытие камеры и клиентского сокета
    cap.release()
    sock.close()
