# import importlib
from testing import *
import xml.etree.ElementTree as ET
# STT = importlib.import_module("VTT")
# TTS = importlib.import_module("TTS")
import PySimpleGUI as sg


class Scene:
    def __init__(self, intents, int_values, name=None, children=None, pass_conditions=None, answer=None, questions=None,
                 theme=None):
        self.name = name
        self.intents = intents
        self.int_values = int_values
        self.children = []
        self.pass_conditions = []
        self.height = 0
        self.answer = answer
        self.questions = []
        self.theme = theme
        if children is not None:
            for child in children:
                self.add_child(child)
        if pass_conditions is not None:
            for condition in pass_conditions:
                self.add_condition(condition)
        if questions is not None:
            for question in questions:
                self.add_condition(question)

    def set_answer(self, answer):
        self.answer = answer

    def set_name(self, name):
        self.name = name

    def set_intents(self, intents):
        self.intents = intents

    def set_int_values(self, int_values):
        self.int_values = int_values

    def add_child(self, node):
        assert isinstance(node, Scene)
        self.children.append(node)

    def add_condition(self, condition):
        self.pass_conditions.append(condition)

    def add_question(self, question):
        self.questions.append(question)

    def print_scene(self):
        print(self.name, self.intents, self.int_values, self.height)

    def print_pretty(self):
        print('---' * self.height, self.name, self.intents, self.int_values, self.height)

    def print_children(self):
        self.print_scene()
        for child in self.children:
            child.print_children()

    def print_pretty_children(self):
        child_counter = 0
        while child_counter < len(self.children) / 2:
            self.children[child_counter].print_pretty_children()
            child_counter += 1
        self.print_pretty()
        while child_counter < len(self.children):
            self.children[child_counter].print_pretty_children()
            child_counter += 1

    def set_height(self, height):
        self.height = height
        return height + 1

    def set_height_all(self, height):
        new_height = self.set_height(height)
        for child in self.children:
            child.set_height_all(new_height)

    def print_answer(self):
        answer = ''
        for ans in self.answer:
            answer += ' ' + ans
        answer += ' '
        print(answer)

    '''
    def passScene(self, intents):
        try:
            children_index = self.pass_conditions.index(intents)
            return self.children[children_index]
        except ValueError:
            return False
    '''

    def conv_continue(self, cur_intents):
        str_int = ' '.join(cur_intents)
        send_log(str_int, self.name)
        weights_list = []
        for idx, condition in enumerate(self.pass_conditions):
            children_weight = 0
            for part_condition in condition:
                if part_condition in cur_intents:
                    children_weight += 1
            weights_list.append(children_weight)

        scene_index = weights_list.index(max(weights_list))
        if max(weights_list) == 0:
            return False
        else:
            send_log('answer', self.children[scene_index].name)
            send_res('OK')
            # self.children[scene_index].print_scene()
            return self.children[scene_index]


class SceneTree:
    def __init__(self, root):
        self.root = root

    def print_nodes(self):
        self.root.print_children()

    def print_pretty_nodes(self):
        self.root.print_pretty_children()

    def set_height_tree(self):
        self.root.set_height_all(0)

    def conv_rec(self, cur_intents, scene):
        if scene.conv_continue(cur_intents):
            scene = scene.conv_continue(cur_intents)
        return scene

    def start_conversation(self):
        cur_intents = []
        new_intent = ''
        scene = self.root
        while new_intent != 'stop':
            print('Введите intent:')
            new_intent = input()
            cur_intents.append(new_intent)
            # self.root.conv_continue(cur_intents)
            scene = self.conv_rec(cur_intents, scene)
            scene.print_scene()

        return True


def window_tree(tree):
    layout = [
        [sg.Text("Hello from PySimpleGUI")],
        [sg.Button("Вывести дерево")],
        [sg.Button("Перейти в сцену")]
        [sg.Output(size=(100, 10), key='-Output-')],
        [sg.Button("Закрыть")],
        [sg.Button("Очистить")]
    ]

    window = sg.Window("Demo", layout)

    while True:
        event, values = window.read()
        if event == "Вывести дерево":
            tree.print_pretty_nodes()
        if event == "Очистить":
            window['-Output-'].update('')
        if event == "Закрыть" or event == sg.WIN_CLOSED:
            break

    window.close()


def main():
    # TTS.speak('проверка')
    # TTS.speak('текст')
    # print(STT.listen())

    main_scene = Scene(intents=['главный'], int_values=['значение'], name='main', answer=['a', 'intent', 'b'],
                       pass_conditions=[['pass']])
    # 'intent' менять на list intents
    sub1 = Scene(intents=['первый'], int_values=['значение'], name='sub1', pass_conditions=[['one']])
    sub2 = Scene(intents=['второй'], int_values=['значение'], name='sub2', pass_conditions=[['two, three']])
    sub12 = Scene(intents=['первый второй'], int_values=['значение'], name='sub12')
    tree = SceneTree(main_scene)
    main_scene.add_child(sub1)
    main_scene.add_child(sub2)
    sub1.add_child(sub12)
    tree.set_height_tree()
    main_scene.print_scene()
    tree.print_nodes()
    print('---')
    tree.print_pretty_nodes()
    main_scene.print_answer()

    tree = ET.parse('info.xml')
    root = tree.getroot()
    to_print = root.findall("intent")
    for tag in to_print:
        print(tag.text)

    # sg.Window(title="tree_print", layout=[[]], margins=(200, 100)).read()
    # window_tree(tree)

    cur_intents = ['pass', 'one', 'two', 'three']

    return 0


if __name__ == '__main__':
    main()
