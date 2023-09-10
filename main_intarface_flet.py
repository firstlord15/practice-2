import sys
import time
import flet as ft
import psycopg2
from config import db_config_main, NAME_PROGRAMM, ICON_PATH


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


def main(page: ft.Page):
    page.title = NAME_PROGRAMM
    page.window_center()
    page.scroll = True
    data_size = 80

    col_items = 30
    min_pages = 1
    page.num_page = 1

    start = time.time()  # точка отсчета времени
    # Подключение к базе данных
    conn = psycopg2.connect(**db_config_main)
    cursor = conn.cursor()

    # Выполнение запроса для извлечения данных из таблицы
    query = "SELECT * FROM access_logs"
    cursor.execute(query)

    rows = cursor.fetchall()

    max_pages, remainder = divmod(len(rows), col_items)
    if remainder > 0:
        max_pages += 1

    # # Получение списка названий столбцов
    # column_names = [desc[0] for desc in cursor.description]

    # Получение списка уникальных IP-адресов
    unique_ips = set(row[2] for row in rows)

    # Закрытие соединения с базой данных
    cursor.close()
    conn.close()

    # DataTable в странице Flet
    datatable = ft.DataTable(
        width=1300,
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Title_status_log")),
            ft.DataColumn(ft.Text("Ip_address")),
            ft.DataColumn(ft.Text("Request_time")),
            ft.DataColumn(ft.Text("Request_path")),
            ft.DataColumn(ft.Text("Status_code")),
            ft.DataColumn(ft.Text("Response_size")),
        ],
    )

    def FixSizeString(data):
        result = ""
        
        if not isinstance(data, str):
            data = str(data)

        if len(data) > data_size:
            result = data[0:data_size-1] + "..."
        else:
            result = data
        return result

    rows_list = []

    for cartej in rows:
        id = FixSizeString(cartej[0])
        title_status_log = FixSizeString(cartej[1])
        ip_address = FixSizeString(cartej[2])
        request_time = FixSizeString(cartej[3])
        request_path = FixSizeString(cartej[4])
        status_code = FixSizeString(cartej[5])
        response_size = FixSizeString(cartej[6])
        row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(id))),  # ID
                ft.DataCell(ft.Text(str(title_status_log))),  # Title_status_log
                ft.DataCell(ft.Text(str(ip_address))),  # iP_address
                ft.DataCell(ft.Text(str(request_time))),  # Request_time
                ft.DataCell(ft.Text(str(request_path))),  # Request_path
                ft.DataCell(ft.Text(str(status_code))),  # Status_code
                ft.DataCell(ft.Text(str(response_size))),  # Response_size
            ],
        )

        rows_list.append(row)

    def AppendRowsDatatable(dtable):
        dtable.rows.clear()
        for count in range(col_items * (page.num_page - 1), col_items * page.num_page):
            if count < len(rows_list):
                dtable.rows.append(rows_list[count])
        page.update()

    def StartAppendRowsDatatable(dtable):
        for count in range(col_items):
            dtable.rows.append(rows_list[count])
        page.update()

    StartAppendRowsDatatable(datatable)

    def next(e):
        if page.num_page < max_pages:
            page.num_page += 1
        AppendRowsDatatable(datatable)



    def prev(e):
        if not page.num_page <= min_pages:
            page.num_page -= 1
        AppendRowsDatatable(datatable)

    # Dropdawn для уникальных IP
    ip_dropdawn = ft.Dropdown(hint_text="Уникальный IP для фильтра", width=1000)
    ip_dropdawn.options.append(ft.dropdown.Option("None"))

    for elenments in unique_ips:
        ip_dropdawn.options.append(ft.dropdown.Option(elenments))

    # Кнопки интерфейса
    btn_date_sort = ft.FilledButton(text="Сортировка по дате", width=500)
    btn_ip_sort = ft.ElevatedButton(text="Сортировка по IP", width=500)
    activte = ft.ElevatedButton(text="Применить фильтр", width=500)
    save_json_file = ft.ElevatedButton(text="Сохранить в json файле", width=500)

    # Кнопки для перехода 
    prev_button = ft.FloatingActionButton(text="Назад", width=500, on_click=prev)
    next_button = ft.FloatingActionButton(text="Вперед", width=500, on_click=next)

    # Добавления объектов на страницу в определенном порядке
    centered_content = ft.Column(
        [
            ft.Row([datatable], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([prev_button, next_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([btn_ip_sort, btn_date_sort], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([activte, save_json_file], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([ip_dropdawn], alignment=ft.MainAxisAlignment.CENTER)
        ],
    )
    page.add(centered_content) # Добавлении основного контейнера
    end = time.time() - start  # Собственно время работы программы
    print("time:", end)  # Вывод времени


if __name__ == "__main__":
    check()
    ft.app(target=main, view=ft.FLET_APP)  # открытие программы
