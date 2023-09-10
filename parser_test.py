import pandas as pd
import xarray as xr
import time
import sys
import psycopg2
from config import db_config_main, NAME_PROGRAMM


def check():
    conn = psycopg2.connect(**db_config_main)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM access_logs")
    result = cursor.fetchone()
    record_count = result[0]  # Количество записей в таблице

    cursor.close()
    conn.close()

    if record_count == 0:
        # Если база данных пуста, показываем сообщение
        print('База данных пуста. Открытие приложения невозможно.')
        sys.exit()


def main():
    output = ""
    i = 0
    # Подключение к базе данных
    conn = psycopg2.connect(**db_config_main)
    cursor = conn.cursor()

    # Выполнение запроса для извлечения данных из таблицы
    query = "SELECT * FROM access_logs"
    cursor.execute(query)

    data = cursor.fetchall()

    for row in data:
        output += f"ID: {row[0]}, " \
                  f"\nTitle: {row[1]}, " \
                  f"\nIP: {row[2]}, " \
                  f"\nRequest time: {row[3]} " \
                  f"\nRequest path: {row[4]}, " \
                  f"\nStatus code: {row[5]}, " \
                  f"\nResponse size: {row[6]}" \
                  f"\n\n\n\n"
        i += 1

    answer = input("\n1 or 2? "
                   "\n> ")
    if answer == "1":
        print(output)
    else:
        print(f"count: {i}")

    # Закрытие соединения с базой данных
    cursor.close()
    conn.close()


if __name__ == "__main__":
    check()
    start = time.time()  # точка отсчета времени
    main()  # открытие программы
    end = time.time() - start  # собственно время работы программы
    print("time:", end)  # вывод времени
