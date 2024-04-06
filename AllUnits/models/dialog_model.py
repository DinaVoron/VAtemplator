# from app import graph
from models.editor_data_model import send_log
import pickle as pc
import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


class IntentTemplate:
    def __init__(self, name, idx = None, has_value = True):
        self.name = name
        self.has_value = has_value


class IntentValue:
    def __init__(self, name, value = None):
        self.name = name
        self.value = value


class Scene:
    def __init__(self, name = None, children = None, pass_conditions = None,
                 answer = None, questions = None, theme = None):
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

    def get_pretty(self):
        return ("---" * self.height + self.name + ", " +
                str(self.height) + "\n")

    def print_pretty_children(self):
        child_counter = 0
        while child_counter < len(self.children) / 2:
            self.children[child_counter].print_pretty_children()
            child_counter += 1
        self.print_pretty()
        while child_counter < len(self.children):
            self.children[child_counter].print_pretty_children()
            child_counter += 1

    def get_pretty_children(self, all_scenes):
        child_counter = 0
        while child_counter < len(self.children) / 2:
            all_scenes = (self.children[child_counter].
                          get_pretty_children(all_scenes))
            child_counter += 1
        all_scenes += self.get_pretty()
        while child_counter < len(self.children):
            all_scenes = (self.children[child_counter].
                          get_pretty_children(all_scenes))
            child_counter += 1
        return all_scenes

    def set_height(self, height):
        self.height = height
        return height + 1

    def set_height_all(self, height):
        new_height = self.set_height(height)
        for child in self.children:
            child.set_height_all(new_height)

    def print_answer(self):
        answer = ""
        for ans in self.answer:
            answer += " " + ans
        answer += ' '
        print(answer)

    # intents_dicts - лист словарей
    def give_answer(self, intents_dicts):
        answer = ""
        for ans in self.answer:
            if isinstance(ans, IntentTemplate):
                for intent in intents_dicts:
                    if intent.get("intent") == ans.name:
                        answer += ' ' + intent.get("intent")
            elif isinstance(ans, IntentValue):
                for intent in intents_dicts:
                    if intent.get("intent") == ans.name:
                        answer += ' ' + intent.get("meaning")
            else:
                answer += " " + ans

        return answer

    def conv_continue(self, cur_intents):
        str_int = " ".join(cur_intents)
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
                intent_idx = idx
                for idx2, elem in enumerate(question):
                    if ((type(elem) == IntentTemplate) and
                            (idx2 == intent_idx)):
                        elem.idx = idx
                        intent_values = (self.get_intent_values
                                         (elem.name,
                                          user_question_list, question))
                        if not intent_values:
                            intent_dict.append({"intent": elem.name,
                                                    "meaning": None})
                        else:
                            intent_dict.append({"intent": elem.name,
                                                    "meaning": intent_values})
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
                if child.to_scene_rec(scene_name):
                    return child.to_scene_rec(scene_name)

    # Поиск сцены по интентам в вопросах(в виде строк)
    # Необходимо наличие всех в вопросе
    def check_scene_rec(self, intents):
        intents.sort()
        for question in self.questions:
            checklist = []
            for word in question:
                if isinstance(word, IntentTemplate):
                    if word.name in intents:
                        checklist.append(word.name)
            # оставлены только уникальные интенты
            checklist = list(set(checklist))
            checklist.sort()
            if checklist == intents:
                return self.name
        for child in self.children:
            return child.check_scene_rec(intents)

# Поиск сцены по интентам и переходам
    def pass_to_children(self, intents):
        intents.sort()
        for pass_cond in self.pass_conditions:
            checklist = []
            for int in pass_cond:
                if int in intents:
                    checklist.append(int.name)
            # оставлены только уникальные интенты
            checklist = list(set(checklist))
            checklist.sort()
            if checklist == intents:
                return self.name
        for child in self.children:
            return child.pass_to_children(intents)


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

    def get_pretty_nodes(self):
        all_scenes = ""
        all_scenes += self.root.get_pretty_children(all_scenes)
        return all_scenes


    def start_conversation_old(self):
        cur_intents = []
        scene = self.root
        print("Введите intent:")
        new_intent = input()
        while new_intent != "stop":
            cur_intents.append(new_intent)
            scene = self.conv_rec(cur_intents, scene)
            scene.print_scene()
            print("Введите intent:")
            new_intent = input()

        return True

    # Диалог
    def start_conversation(self, istext = True):
        scene = self.root
        print("Введите или задайте вопрос")
        if istext:
            question = input()
        else:
            question = take_command()

        while question != "стоп":
            intent_list_dictionary = scene.get_work_question(question)
            if (intent_list_dictionary): # Если найдены шаблоны
                # Отправить в граф
                # Получить из графа
                # Вернуть ответ
                intents = []
                for intent in intent_list_dictionary:
                    intents.append(intent.get("intent"))
                scene.pass_to_children(intents)
            else:
                # Уточняющий вопрос
                pass

            print("Введите или задайте вопрос")
            if istext:
                question = input()
            else:
                question = take_command()

        return True

    def scene_add(self, parent_scene, name = None, children = None,
                  pass_conditions = None, answer = None, questions = None,
                  theme = None):
        new_scene = Scene(name = name, children = children,
                          pass_conditions = pass_conditions, answer = answer,
                          questions = questions, theme = theme)
        parent_scene.add_child(new_scene)
        return new_scene

    def find_scene(self, intents):
        self.root.check_scene_rec(intents)


def main():
    # Десериализация pickle
    with open("save_files/pickle_test.PKL", "rb") as f:
        tree = pc.load(f)

    '''
    main_scene = Scene(name="main", answer=["a", "intent", "b"], 
    pass_conditions=[["pass"]],
                       questions=[[IntentTemplate("направление"), 
                       "значение", IntentValue("направление"),
                                   IntentValue("направление"), 
                                   IntentTemplate("балл")]])
    sub1 = Scene(name="sub1", pass_conditions=[["one"]])
    sub2 = Scene(name="sub2", pass_conditions=[["two, three"]])
    sub21 = Scene(name="sub21", pass_conditions=[["one"]])
    sub12 = Scene(name="sub12")
    tree = SceneTree(main_scene)
    main_scene.add_child(sub1)
    main_scene.add_child(sub2)
    sub1.add_child(sub12)
    sub2.add_child(sub21)
    tree.set_height_tree()
    # main_scene.print_scene()
    # tree.print_nodes()
    # print("---")
    # tree.print_pretty_nodes()
    # main_scene.print_answer()

    print(main_scene.check_scene_rec(["направление", "балл"]))
    '''

    # Сериализация pickle
    with open("save_files/pickle_test.PKL", "wb") as f:
        pc.dump(tree, f)

    return tree



def get_scenes():
    res = []
    get_scene(dialog_tree.root, res)
    return res


def get_scene(node, res):
    res.append(node)
    for child in node.children:
        get_scene(child, res)


def get_text_scenes(dialog_tree):
    return dialog_tree.get_pretty_nodes()


def get_root(dialog_tree):
    return dialog_tree.root

def get_scene_name(cur_scene):
    return cur_scene.name

def find_scene_by_name(name, dialog_tree):
    return dialog_tree.to_scene(name)

def get_scene_everything(current_scene):
    stats = [
        current_scene.children,
        current_scene.pass_conditions,
        current_scene.answer,
        current_scene.questions
    ]
    return stats


def add_child(current_scene, child_scene, dialog_tree):
    current_scene.add_child(child_scene)
    dialog_tree.set_height_tree()


def add_scene(name, parent, pass_conditions, answer, questions):
    # Условия перехода пока одной строкой с разделением |
    pass_conditions_normal = []
    pass_condition = []
    pass_conditions_list = pass_conditions.split(' ')
    for word in pass_conditions_list:
        if word == '|':
            pass_conditions_normal.append(pass_condition)
            pass_condition = []
        else:
            pass_condition.append(word)
    pass_conditions_normal.append(pass_condition)

    # Ответ - лист слов до ввода графа,
    # todo: отделить интенты и значения от слов
    answer = answer.split()

    # Вопросы - аналогично условиям перехода, IT - следующее слово будет...
    # объектом интента, IV - аналогично значение
    questions_normal = []
    question = []
    questions_list = questions.split(' ')
    next_intent = False
    next_value = False
    for word in questions_list:
        if next_intent:
            question.append(tree.IntentTemplate(word))
            next_intent = False
        elif next_value:
            question.append(tree.IntentValue(word))
            next_value = False
        else:
            if word == '|':
                questions_normal.append(question)
                question = []
            elif word == 'IT':
                next_intent = True
            elif word == 'IV':
                next_value = True
            else:
                question.append(word)
    questions_normal.append(question)

    to_add = tree.Scene(name=name, pass_conditions=pass_conditions_normal,
                        answer=answer, questions=questions_normal)
    parent_scene = dialog_tree.to_scene(parent)
    parent_scene.add_child(to_add)
    dialog_tree.set_height_tree()

    return to_add


def save_tree(file):
    with open(file, "wb") as f:
        pc.dump(dialog_tree, f)


def take_command():
    r = sr.Recognizer()

    with sr.Microphone() as source:

        print("Слушаем...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Распознаем...")
        query = r.recognize_google(audio, language="ru-RU")
        print({query})

    except Exception as e:
        print(e)
        print("Unable to Recognize your voice.")
        return "Не распознано. Попробуйте еще раз."

    return query


# Текст вопроса - текст ответа
def ask_question(current_scene, question_text):
    question_intent_dict = current_scene.get_work_question(question_text)
    if (question_intent_dict):
        question_intent_dict = graph.search(question_intent_dict)
    answer = current_scene.give_answer(question_intent_dict)
    return answer


def intent_dict_to_list(intent_dict):
    intent_list = []
    if (not intent_dict):
        intent_dict = []
    for intent in intent_dict:
        int_name = intent.get("intent")
        intent_list.append(int_name)
    return intent_list


# Переход к следующей сцене (возможен переход сразу через несколько)
def pass_scene(cur_scene, cur_intents_list):
    new_scene_name = cur_scene.pass_to_children(cur_intents_list)
    return new_scene_name


# Ответ, новая сцена, словарь интентов и значений, лист интентов
def dialog(current_scene, question_text):
    answer = ask_question(current_scene, question_text)
    question_intent_dict = current_scene.get_work_question(question_text)
    send_log(question_text, question_intent_dict, current_scene.name)
    send_log(answer, False, current_scene.name)
    if (question_intent_dict):
        question_intent_dict = graph.search(question_intent_dict)
    intent_list = intent_dict_to_list(question_intent_dict)
    new_scene_name = pass_scene(current_scene, intent_list)
    return [answer, new_scene_name, question_intent_dict, intent_list]