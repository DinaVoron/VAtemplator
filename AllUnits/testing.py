# from debug import set_debug
import pymorphy3
from datetime import date
import datetime
from tree import *
import re
import xml.etree.ElementTree as ET


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





def plug_dialog(questions, answers, question):
    index = questions.index(question)
    return answers[index]





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





