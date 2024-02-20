import numpy as np

from data_base_connect import connection


def get_users_data(face_descriptor):
    cursor = connection.cursor()

    # Выполним SQL-запрос для получения данных
    cursor.execute("""SELECT last_name, first_name, patronymic, university_name, face_encoding, photo FROM Persons""")

    # Получаем результаты запроса
    rows = cursor.fetchall()

    user_data = []

    for i, descriptor in enumerate(face_descriptor):
        for j, data_base_user_data in enumerate(rows):
            data_base_descriptor = np.frombuffer(data_base_user_data[4], dtype=np.float64)
            # print(i, descriptor)
            # print(j, data_base_descriptor)
            distance = np.linalg.norm(np.array(data_base_descriptor) - np.array(descriptor))
            print(f"Дистанция = {distance}")
            if 0.55 >= distance:
                user_data.append([data_base_user_data[0], data_base_user_data[1], data_base_user_data[2],
                                  data_base_user_data[3], bytes(data_base_user_data[5])])
                break

    return user_data

