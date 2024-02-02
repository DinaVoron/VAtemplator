import PySimpleGUI as sg


def create_tab1_layout():
    layout = [
        [sg.Button("Вывести дерево", button_color='#ffffff on #17C3CE', border_width=0, font="Inter 12 bold")],
        [sg.InputText()],
        [sg.Button("Найти интенты вопроса")],
        [sg.Button("Перейти в сцену")],
        [sg.Output(size=(100, 10), key="-Output-")],
        [sg.Button("Закрыть")],
        [sg.Button("Очистить")],
        [sg.Button("Перейти к модулю тестирования")]
    ]
    return layout


def create_tab2_layout():
    layout = [
        [sg.Text("Статистика работы")],
        [sg.Text("Успех"), sg.Text("Провал"), sg.Text("Ошибка")]
    ]
    return layout


def create_tab3_layout():
    layout = [
        [sg.Text("Содержимое вкладки 3")],
        [sg.Button("Назад")]
    ]
    return layout

