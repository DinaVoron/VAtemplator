from testing import *
import pickle as pc
import PySimpleGUI as sg
import pyttsx3
import speech_recognition as sr
from interface import *
from graph import *
import subprocess

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)

# заглушка базы данных интентов
global_intents = ["балл", "направление"]


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def take_command():
    r = sr.Recognizer()

    with sr.Microphone() as source:

        print("Слушаем...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Распознаем...")
        query = r.recognize_google(audio, language="ru-RU")
        print("{query}\n")

    except Exception as e:
        print(e)
        print("Unable to Recognize your voice.")
        return "None"

    return query


class IntentTemplate:
    def __init__(self, name, idx=None, has_value=True):
        self.name = name
        self.has_value = has_value


class IntentValue:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value


class Scene:
    def __init__(self, name=None, children=None, pass_conditions=None, answer=None, questions=None,
                 theme=None):
        self.name = name
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
                self.add_question(question)

    def set_answer(self, answer):
        self.answer = answer

    def set_name(self, name):
        self.name = name

    def add_child(self, node):
        assert isinstance(node, Scene)
        self.children.append(node)

    def add_condition(self, condition):
        self.pass_conditions.append(condition)

    def add_question(self, question):
        self.questions.append(question)

    def print_scene(self):
        print(self.name, self.height)

    def print_pretty(self):
        print('---' * self.height, self.name, self.height)

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

    def send_intents(self, intents_and_values):
        # Отправка интентов в семантическую сеть
        pass

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
            send_log("answer", self.children[scene_index].name)
            send_res("OK")
            # self.children[scene_index].print_scene()
            return self.children[scene_index]

    # Обработка вопроса пользователя
    # Пока intent всегда перед значением
    def get_work_question(self, user_question):
        user_question_list = user_question.split()
        # привести к начальной форме через PyMorphy (3)
        intent_dict = []
        intent_count = 0
        for question in self.questions:
            for elem in question:
                if type(elem) == IntentTemplate:
                    intent_count += 1
            for idx, user_word in enumerate(user_question_list):
                if user_word in global_intents:
                    intent_idx = idx
                    for idx2, elem in enumerate(question):
                        if (type(elem) == IntentTemplate) and (idx2 == intent_idx):
                            print(elem.name)
                            elem.idx = idx
                            intent_values = self.get_intent_values(elem.name, user_question_list, question)
                            if intent_values == []:
                                intent_dict.append({"intent": elem.name, "meaning": None})
                            else:
                                intent_dict.append({"intent": elem.name, "meaning": intent_values})
                                # intent_dict[elem.name] = intent_values
                            intent_count -= 1

            if intent_count == 0:
                return intent_dict
            else:
                intent_count = 0

        return False

    def get_intent_values(self, name, user_question_list, question):
        values_list = []
        for idx2, word2 in enumerate(question):
            if type(word2) == IntentValue:
                if word2.name == name:
                    for idx, word in enumerate(user_question_list):
                        if idx2 == idx:
                            values_list.append(word)
        return values_list

    def to_scene_rec(self, scene_name):
        if self.name == scene_name:
            return self
        else:
            for child in self.children:
                return child.to_scene_rec(scene_name)


class SceneTree:
    def __init__(self, root):
        self.root = root

    def to_scene(self, scene_name):
        return self.root.to_scene_rec(scene_name)

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
        print("Введите intent:")
        new_intent = input()
        while new_intent != "stop":
            cur_intents.append(new_intent)
            # self.root.conv_continue(cur_intents)
            scene = self.conv_rec(cur_intents, scene)
            scene.print_scene()
            print("Введите intent:")
            new_intent = input()

        return True

    def scene_add(self, parent_scene, name=None, children=None, pass_conditions=None, answer=None, questions=None,
                 theme=None):
        new_scene = Scene(name=name, children=children, pass_conditions=pass_conditions, answer=answer,
                          questions=questions, theme=theme)
        parent_scene.add_child(new_scene)
        return new_scene


def window_tree(tree):
    layout = [
        [sg.TabGroup([[sg.Tab('Диалог', create_tab1_layout(), key='-TAB1-', background_color='#ffffff'),
        sg.Tab('Тесты', create_tab2_layout(), key='-TAB2-', background_color='#ffffff'),
        sg.Tab('Сеть', create_tab3_layout(), key='-TAB3-', background_color='#ffffff')]], tab_location='lefttop',
                     background_color='#ffffff')]
    ]

    window = sg.Window("Demo", layout, background_color='#ffffff')
    # event, values = window.read()

    while True:
        event, values = window.read()
        text_input = values[0]
        if event == "Вывести дерево":
            tree.print_pretty_nodes()
        if event == "Очистить":
            window["-Output-"].update('')
        if event == "Закрыть" or event == sg.WIN_CLOSED:
            break
        if event == "Найти интенты вопроса":
            print(tree.root.get_work_question(text_input))
        if event == "Перейти в сцену":
            cur_scene = tree.to_scene(text_input)
            print(cur_scene.name)
        if event == "Перейти к модулю тестирования":
            window.close()
            break
        if event == "ok_log":
            subprocess.Popen(["notepad", "controllers/OK.log"])
        if event == "nf_log":
            subprocess.Popen(["notepad", "controllers/NF.log"])
        if event == "err_log":
            subprocess.Popen(["notepad", "controllers/ERR.log"])
        if event == "autotest":
            window["-Output-autotest-"].update(automatic_testing())


    window.close()


text = """
Проходной балл по направлению подготовки "Прикладная математика и информатика" в 2020 году составил 197 баллов.
Проходной балл по направлению подготовки "Прикладная математика и информатика" в 2021 году составил 211 баллов.
Проходной балл по направлению подготовки "Прикладная математика и информатика" в 2022 году составил 200 баллов.
Проходной балл по направлению подготовки "Прикладная математика и информатика" в 2023 году составил 230 баллов.
В 2020 году по направлению подготовки "Математика и компьютерные науки" проходной балл равен 190.
В 2021 году по направлению подготовки "Математика и компьютерные науки" проходной балл равен 172.
В 2022 году по направлению подготовки "Математика и компьютерные науки" проходной балл равен 204.
В 2023 году по направлению подготовки "Математика и компьютерные науки" проходной балл равен 200.

"""

def main():
    main_scene = Scene(name="main", answer=["a", "intent", "b"], pass_conditions=[["pass"]],
                       questions=[[IntentTemplate("направление"), "значение", IntentValue("направление"),
                                   IntentValue("направление"), IntentTemplate("балл")]])
    sub1 = Scene(name="sub1", pass_conditions=[["one"]])
    sub2 = Scene(name="sub2", pass_conditions=[["two, three"]])
    sub12 = Scene(name="sub12")
    tree = SceneTree(main_scene)
    main_scene.add_child(sub1)
    main_scene.add_child(sub2)
    sub1.add_child(sub12)
    tree.set_height_tree()
    main_scene.print_scene()
    tree.print_nodes()
    print("---")
    tree.print_pretty_nodes()
    main_scene.print_answer()

    graph = init_graph()
    graph = graph_nlp_text(graph, text)

    # window_tree(tree)

    cur_intents = ["pass", "one", "two", "three"]

    return tree


if __name__ == "__main__":
    main()
