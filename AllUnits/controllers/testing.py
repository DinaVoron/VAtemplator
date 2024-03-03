import logging
import xml.etree.ElementTree as ET
from debug import set_debug
import pymorphy3
from datetime import date
import datetime
from tree import *
import re


class Node(object):
    def __init__(self, node_id, node_text, node_type):
        self.id = node_id
        self.text = node_text
        self.type = node_type

    def id(self):
        return self.id

    def text(self):
        return self.text


class Link(object):
    def __init__(self, link_start, link_end, link_type):
        self.start = link_start
        self.end = link_end
        self.type = link_type

    def end(self):
        return self.end

    def start(self):
        print(self.start)
        return self.start


def send_log(text, intent_values, place):
    f = open("controllers/temp.log", "a+", encoding="utf-8")
    f.write(log_message(text, intent_values, place) + "\r\n")


def print_info(filename):
    f1 = open('controllers/temp.log', 'r+')
    f2 = open(filename, 'r')
    text = f2.read()
    f2.close()
    text = re.sub("\s*</?logs>\s*", "", text)
    f2 = open(filename, 'w')
    f2.write("<logs>\r\n" + text + "\r\n<log>\r\n" + f1.read() + "</log>\r\n" + "</logs>")
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
    res = "<text>"
    text_split = multi_split(text)
    text_split_normal = []
    for word in text_split:
        text_split_normal.append(morph.parse(word)[0].normal_form)
    for words in intent_values:
        new_words = words.split(" ")
        arr_start = text_split_normal.index(new_words[0])
        arr_end = text_split_normal.index(new_words[len(new_words) - 1])
        text_split[arr_start] = "<intent>" + text_split[arr_start]
        text_split[arr_end] = text_split[arr_end] + "</intent>"
        if intent_values[words] is not None:
            value_arr = str(intent_values[words]).split(" ")
            arr_value_start = text_split_normal.index(morph.parse(str(value_arr[0]))[0].normal_form)
            arr_value_end = text_split_normal.index(morph.parse(str(value_arr[len(value_arr) - 1]))[0].normal_form)
            text_split[arr_value_start] = "<value>" + text_split[arr_value_start]
            text_split[arr_value_end] = text_split[arr_value_end] + "</value>"
    res = res + " ".join(text_split) + "</text>"
    return ("<date>" + str(date.today()) + "</date>" + "<time>" + str(datetime.datetime.now().strftime("%H:%M:%S"))
            + "</time>" + res + "<place>" + place + "</place>")


def multi_split(input_string):
    delimiters = [
        ";", ",", ":",
        ".", "|", "?",
        "\"", " "
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
        case "OK":
            filename = "controllers/OK.log"
            print_info(filename)
        case "ERR":
            filename = "controllers/ERR.log"
            print_info(filename)
        case "NF":
            filename = "controllers/NF.log"
            print_info(filename)


def get_text_question(elem, question):
    for child in elem:
        get_text_question(child, question)
        if child.text is not None and child.text.find('\n'):
            question[0] += child.text + " "


def get_question(filename):
    question = ['']
    tree = ET.parse(filename)
    root = tree.getroot()
    get_text_question(root, question)
    return question[0]


def get_ok(tree, answers, questions):
    root = tree.getroot()
    answer = True
    for log in root:
        answers_arr = []
        questions_arr = []
        reply = log.findall("text")
        for rep in reply:
            if answer:
                answers_arr.append(rep)
            else:
                questions_arr.append(rep)
            answer = not answer
        answers.append(answers_arr)
        questions.append(questions_arr)


def plug_dialog(questions, answers, question):
    index = questions.index(question)
    return answers[index]


def automatic_testing():
    res = 0
    question_arr = []
    answers_arr = []
    # Получаем ответы и вопросы из файла успешного логирования
    tree = ET.parse("controllers/OK.log")
    get_ok(tree, answers_arr, question_arr)
    # Меняем состояние работы на debug
    set_debug(True)
    # Теперь получаем ответ на вопрос для каждого элемента массива, сравниваем с ответами
    q_len = len(question_arr)
    for i in range(q_len):
        if plug_dialog(question_arr, answers_arr, question_arr[i]) == answers_arr[i]:
            res += 1
    return "Успешно пройдено {} из {} тестов!".format(res, q_len)


def graph_verify_try():
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


def find_all_paths(graph, current_node, visited, path, paths):
    visited[current_node] = True
    path.append(current_node)

    for neighbor in graph[current_node]:
        if not visited[neighbor]:
            find_all_paths(graph, neighbor, visited, path, paths)

    paths.append(path.copy())

    visited[current_node] = False
    path.pop()


def find_all_chains(edges):
    graph = {}
    for edge in edges:
        if edge[0] not in graph:
            graph[edge[0]] = []
        if edge[1] not in graph:
            graph[edge[1]] = []

        graph[edge[0]].append(edge[1])
        graph[edge[1]].append(edge[0])

    visited = {node: False for node in graph}
    path = []
    paths = []

    for node in graph:
        find_all_paths(graph, node, visited, path, paths)

    return paths


def graph_verify(graph):
    print("Верификация графа...")
    nodes = graph.nodes
    edges = list(graph.edges)

    chains = find_all_chains(edges)
    for chain in chains:
        print(chain)


def count_errors():
    res = {}
    logs = ET.parse("controllers/ERR.log").getroot()
    for log in logs:
        places = log.findall("place")
        for place in places:
            if place.text in res:
                res[place.text] += 1
            else:
                res[place.text] = 1
    return res



