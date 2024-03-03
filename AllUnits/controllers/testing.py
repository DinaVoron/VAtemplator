import logging
import xml.etree.ElementTree as ET
from debug import set_debug
import pymorphy3
import PySimpleGUI as sg
from tree import *


class Node(object):
    def __init__(self, id, text, type):
        self.id = id
        self.text = text
        self.type = type

    def id(self):
        return self.id

    def text(self):
        return self.text


class Link(object):
    def __init__(self, start, end, type):
        self.start = start
        self.end = end
        self.type = type

    def end(self):
        return self.end

    def start(self):
        print(self.start)
        return self.start


def send_log(text, intent_values, place):
    logging.basicConfig(
        filename='temp.log',
        encoding='utf-8',
        level=logging.INFO,
        force=True,
        format='%(message)s'
    )
    logging.info(log_message(text, intent_values, place))


def print_info(filename):
    f1 = open('temp.log', 'r+')
    f2 = open(filename, 'a+')
    f2.write("<log>" + f1.read() + "</log>")
    f1.truncate(0)
    f1.close()
    f2.close()


def intent_array(intents_values):
    intent_values_new = {}
    if intents_values is not None:
        for i in range(len(intents_values)):
            intent_values_new[intents_values[i]["intent"]] = intents_values[i]["meaning"]
    return intent_values_new


def log_message(text, intents_values_dic, place):
    morph = pymorphy3.MorphAnalyzer()
    intent_values = intent_array(intents_values_dic)
    res = ""
    text_arr = []
    text_split = multi_split(text)
    for word in text_split:
        if morph.parse(word)[0].normal_form in intent_values:
            if len(text_arr) == 0:
                res += "<intent>" + word + "</intent>"
            else:
                res += " ".join(text_arr) + "</text><intent>" + word + "</intent>"
                text_arr = []
        else:
            if len(text_arr) == 0:
                res += "<text>"
                text_arr.append(word)
            else:
                text_arr.append(word)
    if len(text_arr) != 0:
        res += " ".join(text_arr) + "</text>"
    return res + "<place>in " + place + "</place>"


def multi_split(input_string):
    delimiters = [
        ";", ",", ":",
        ".", "|", "?",
        "\""
    ]
    segments = [input_string]
    for delimiter in delimiters:
        new_segments = []
        for segment in segments:
            new_segments.extend(segment.split(delimiter))
            segments = new_segments
    return segments


def send_res(res):
    match res:
        case 'OK':
            filename = 'OK.log'
            print_info(filename)
        case 'ERR':
            filename = 'ERR.log'
            print_info(filename)
        case 'NF':
            filename = 'NF.log'
            print_info(filename)


def get_text_question(elem, question):
    for child in elem:
        get_text_question(child, question)
        if child.text is not None and child.text.find('\n'):
            question[0] += child.text + ' '


def get_question(filename):
    question = ['']
    tree = ET.parse(filename)
    root = tree.getroot()
    get_text_question(root, question)
    return question[0]


def get_ok(answers, questions):
    f1 = open("OK.log", "r")
    lines = f1.readlines()
    cur = 0
    while cur < len(lines):
        if lines[cur][0] == '-':
            cur += 1
            continue
        else:
            answers.append(lines[cur].split(" ")[1])
            cur += 1
            questions.append(lines[cur].split(" ")[1])
            cur += 1


def plug_dialog(questions, answers, question):
    index = questions.index(question)
    return answers[index]


def automatic_testing():
    res = 0
    question_arr = []
    answers_arr = []
    # Получаем ответы и вопросы из файла успешного логирования
    get_ok(answers_arr, question_arr)
    # Меняем состояние работы на debug
    set_debug(True)
    # Теперь получаем ответ на вопрос для каждого элемента массива, сравниваем с ответами
    q_len = len(question_arr)
    for i in range(q_len):
        if plug_dialog(question_arr, answers_arr, question_arr[i]) == answers_arr[i]:
            res += 1
    return "Успешно пройдено {} из {} тестов!".format(res, q_len)


def graph_verify():
    n1 = Node(1, "Балл", "intent")
    n2 = Node(2, "Специальность", "intent")
    n3 = Node(3, "2020", "value")
    n4 = Node(4, "Год", "intent")
    n5 = Node(5, "Программная инженерия", "value")
    n6 = Node(6, "210", "value")

    nodes = [
        n1, n2, n3, n4, n5, n6
    ]

    link1 = Link(2, 5, "DET")
    link2 = Link(5, 4, "ATTR")
    link3 = Link(4, 3, "DET")
    link4 = Link(3, 1, "ATTR")
    link5 = Link(1, 6, "DET")

    smgraph = [
        link1, link2, link3, link4, link5
    ]

    for i in range(len(smgraph)):
        next = smgraph[i].end
        for j in range(i + 1, len(smgraph)):
            if smgraph[j].start == next:
                print("Не хотите добавить вопрос с такими интентами?")
                print(
                    nodes[smgraph[i].start - 1].text
                    + " "
                    + nodes[smgraph[i].end - 1].text
                    + " "
                    + nodes[smgraph[j].end - 1].text)


def window_testing():
    layout = [
        [sg.Button("Начать автоматическое тестирование")],
        [sg.Button("Провести верификацию графа")],
        [sg.Output(size=(100, 10), key="-Output-")],
        [sg.Button("Назад")]
    ]
    window = sg.Window("Модуль тестирования", layout)
    event, values = window.read()
    while True:
        event, values = window.read()
        if event == "Начать автоматическое тестирование":
            print(automatic_testing())
        if event == "Провести верификацию графа":
            print(graph_verify())
        if event == "Закрыть" or event == sg.WIN_CLOSED:
            break
        if event == "Назад":

            window_tree()
            window.close()
            break
    window.close()


