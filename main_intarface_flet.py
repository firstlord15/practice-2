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
    # Насторойка страницы
    page.title = NAME_PROGRAMM
    page.theme_mode = "Light"
    page.window_center()
    page.scroll = True

    start = time.time()  # точка отсчета времени
    # Подключение к базе данных
    conn = psycopg2.connect(**db_config_main)
    cursor = conn.cursor()

    # Выполнение запроса для извлечения данных из таблицы
    query = "SELECT * FROM access_logs"
    cursor.execute(query)

    rows = cursor.fetchall()

    # Переменые с данными
    data_size = 50
    col_items = 30
    min_pages = 1
    page.num_page = 1
    max_pages, remainder = divmod(len(rows), col_items)
    if remainder > 0:
        max_pages += 1

    # Получение списка уникальных IP-адресов
    unique_ips = set(row[2] for row in rows)

    # Закрытие соединения с базой данных
    cursor.close()
    conn.close()

    # DataTable в странице Flet
    datatable = ft.DataTable(
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
        if not isinstance(data, str): data = str(data)
        if len(data) > data_size: result = data[0:data_size-1] + "..."
        else: result = data
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
            ]
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

    def check_page_input(input):
        if input.value.strip() != '':
            pages = int(input.value)
        else:
            input.focus()
            pages = ''
        return pages

    def select_page(e):
        pages = check_page_input(page_input)
        if pages != '':
            if min_pages <= pages <= max_pages:
                page.num_page = pages
        AppendRowsDatatable(datatable)
        

    # Dropdawn для уникальных IP
    # ip_dropdawn = ft.Dropdown(hint_text="Уникальный IP для фильтра", width=1000)
    # ip_dropdawn.options.append(ft.dropdown.Option("None"))

    # for elenments in unique_ips:
    #     ip_dropdawn.options.append(ft.dropdown.Option(elenments))

    # Кнопки интерфейса
    # btn_date_sort = ft.FilledButton(text="Сортировка по дате", width=500)
    # btn_ip_sort = ft.ElevatedButton(text="Сортировка по IP", width=500)
    # activte = ft.ElevatedButton(text="Применить фильтр", width=500)
    # save_json_file = ft.ElevatedButton(text="Сохранить в json файле", width=500)

    # Кнопки для перехода 
    prev_button = ft.FloatingActionButton(text="Назад", width=400, on_click=prev, bgcolor=ft.colors.AMBER_300, shape=ft.RoundedRectangleBorder(radius=5))
    next_button = ft.FloatingActionButton(text="Вперед", width=400, on_click=next, bgcolor=ft.colors.AMBER_300, shape=ft.RoundedRectangleBorder(radius=5))
    page_input = ft.TextField(hint_text="Номер страницы", width=120, border=None, border_radius=5)
    page_button_select = ft.FloatingActionButton(text="Потвердить", width=120, on_click=select_page, shape=ft.RoundedRectangleBorder(radius=5))

    # Добавления объектов на страницу в определенном порядке
    main_container = ft.ResponsiveRow(
        [
            ft.Row([datatable], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            ft.Row([page_input, page_button_select], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            ft.Row([prev_button, next_button], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            # ft.Row([btn_ip_sort, btn_date_sort], alignment=ft.MainAxisAlignment.CENTER),
            # ft.Row([activte, save_json_file], alignment=ft.MainAxisAlignment.CENTER),
            # ft.Row([ip_dropdawn], alignment=ft.MainAxisAlignment.CENTER)
        ],
    )

    tabbar = ft.Tabs(
        selected_index=1,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Tab 1",
                content=ft.Text("This is Tab 1")
            ),
            ft.Tab(
                tab_content=ft.Icon(ft.icons.SEARCH),
                content=main_container,
            ),
            ft.Tab(
                text="Tab 3",
                icon=ft.icons.SETTINGS,
                content=ft.Text("This is Tab 3"),
            ),
        ],
        expand=1,
    )
    
    
    page.add(tabbar) # Добавлении основного контейнера
    end = time.time() - start  # Собственно время работы программы
    print("time:", end)  # Вывод времени


if __name__ == "__main__":
    check()
    ft.app(target=main, view=ft.FLET_APP)  # открытие программы
