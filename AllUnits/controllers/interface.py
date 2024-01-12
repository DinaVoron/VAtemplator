import PySimpleGUI as sg


def create_tab1_layout():
    layout = [
        [sg.Button("Вывести дерево")],
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
        [sg.Text("Содержимое вкладки 2")],
        [sg.Button("Назад")]
    ]
    return layout


def create_tab3_layout():
    layout = [
        [sg.Text("Содержимое вкладки 3")],
        [sg.Button("Назад")]
    ]
    return layout
