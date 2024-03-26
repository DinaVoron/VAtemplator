# import PySimpleGUI as sg
# from testing import *
# import subprocess
# import xml.etree.ElementTree as ET
#
#
# def create_tab1_layout():
#     layout = [
#         [sg.Button("Вывести дерево",
#                    button_color='#ffffff on #17C3CE',
#                    border_width=0, font="Inter 12 bold")],
#         [sg.InputText()],
#         [sg.Button("Найти интенты вопроса")],
#         [sg.Button("Перейти в сцену")],
#         [sg.Output(size=(100, 10), key="-Output-")],
#         [sg.Button("Закрыть")],
#         [sg.Button("Очистить")],
#         [sg.Button("Перейти к модулю тестирования")]
#     ]
#     return layout
#
#
# def create_tab2_layout():
#     success_amount = len(ET.parse("controllers/OK.log").getroot())
#     not_found_amount = len(ET.parse("controllers/NF.log").getroot())
#     error_amount = len(ET.parse("controllers/ERR.log").getroot())
#     all_amount = success_amount + not_found_amount + error_amount
#     success_div = [
#         [sg.Text("Успех",
#                  background_color="#EAFFF2",
#                  text_color="#000000")],
#         [sg.Text("{}/{} диалогов".format(success_amount, all_amount),
#                  background_color="#EAFFF2", text_color="#919191")],
#         [sg.Button("Посмотреть логи",
#                    button_color="#000000 on #B3EBDE",
#                    border_width=0, key="ok_log")]
#     ]
#     not_found_div = [
#         [sg.Text("Провал", background_color="#FFEAEA",
#                  text_color="#000000")],
#         [sg.Text("{}/{} диалогов".format(not_found_amount, all_amount),
#                  background_color="#FFEAEA", text_color="#919191")],
#         [sg.Button("Посмотреть логи",
#                    button_color="#000000 on #f6baba",
#                    border_width=0, key="nf_log")]
#     ]
#     error_div = [
#         [sg.Text("Ошибка",
#                  background_color="#8DF7FF",
#                  text_color="#000000")],
#         [sg.Text("{}/{} диалогов".format(error_amount, all_amount),
#                  background_color="#8DF7FF", text_color="#919191")],
#         [sg.Button("Посмотреть логи",
#                    button_color="#000000 on #28BFCB",
#                    border_width=0, key="err_log")]
#     ]
#     layout = [
#         [sg.Text("Статистика работы",
#                  background_color="#ffffff",
#                  text_color="#000000", font="bold")],
#         [
#             sg.Column(success_div,
#                       element_justification="l",
#                       background_color="#EAFFF2"),
#             sg.Column(not_found_div,
#                       element_justification="l",
#                       background_color="#FFEAEA"),
#             sg.Column(error_div,
#                       element_justification="l",
#                       background_color="#8DF7FF")
#         ],
#         [sg.Text("Автоматическое тестирование",
#                  background_color="#ffffff",
#                  text_color="#000000",
#                  font="bold")],
#         [sg.Button("Начать",
#                    key="autotest",
#                    button_color="#ffffff on #17C3CE",
#                    font="bold")],
#         [sg.Multiline(no_scrollbar=True,
#                       key="-Output-autotest-",
#                       background_color="#ffffff",
#                       border_width=0)],
#         [sg.Text("Возможные вопросы",
#                  background_color="#ffffff",
#                  text_color="#000000",
#                  font="bold")],
#         [sg.Multiline(size=(100, 10),
#                       key="-Output-verify-",
#                       no_scrollbar=True,
#                       background_color="#ffffff",
#                       border_width=0)]
#     ]
#     return layout
#
#
# def create_tab3_layout():
#     layout = [
#         [sg.Text("Содержимое вкладки 3")],
#         [sg.Button("Назад")]
#     ]
#     return layout


# def window_testing():
#     event, values = window.read()
#     while True:
#         event, values = window.read()
#
#         if event == "Начать автоматическое тестирование":
#             print(automatic_testing())
#         if event == "Провести верификацию графа":
#             print(graph_verify())
#         if event == "Закрыть" or event == sg.WIN_CLOSED:
#             break
#         if event == "Назад":
#
#             window_tree()
#             window.close()
#             break
#     window.close()
