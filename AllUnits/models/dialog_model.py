from models.graph_model import Graph
from models.editor_data_model import send_log
import pickle as pc
import speech_recognition as sr
import pyttsx3
import pymorphy3

morph = pymorphy3.MorphAnalyzer()
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


class IntentTemplate:
    def __init__(self, name, idx=None, has_value=True):
        self.name = name
        self.has_value = has_value


class IntentValue:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value


class Scene:
    def __init__(self, name = None, children = None, pass_conditions = None,
                 answer = None, questions = None,
                 clarifying_question = None, available_intents_list = None):
        self.name = name
        self.children = []
        self.pass_conditions = []
        self.height = 0
        self.answer = answer
        self.questions = []
        self.clarifying_question = clarifying_question
        self.available_intents_list = available_intents_list
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
        answer = answer.removesuffix(' | ')
        answer_list = answer.split(' | ')
        answer_list_final = []
        for answer_word in answer_list:
            if "Интент" in answer_word:
                answer_list_final.append(IntentTemplate(name=answer_word.split("Интент ")[1]))
            elif "Значение" in answer_word:
                answer_list_final.append(IntentValue(name=answer_word.split("Значение ")[1]))
            else:
                answer_list_final.append(answer_word)

        self.answer = answer_list_final

    def set_question(self, question):
        question = question.removesuffix(' | ')
        question_list = question.split(' | ')
        question_list_final = []
        for question_word in question_list:
            if "Интент" in question_word:
                question_list_final.append(
                    IntentTemplate(name=question_word.split("Интент ")[1]))
            else:
                question_list_final.append(
                    IntentValue(name=question_word.split("Значение ")[1]))
        self.question = question_list_final

    def set_name(self, name):
        self.name = name

    def set_clarifying_question(self, clarifying_question):
        clarifying_question = clarifying_question.removesuffix(' | ')
        question_list = clarifying_question.split(' | ')
        question_list_final = []
        for question_word in question_list:
            if "Интент" in question_word:
                question_list_final.append(
                    IntentTemplate(name=question_word.split("Интент ")[1]))
            elif "Значение" in question_word:
                question_list_final.append(
                    IntentValue(name=question_word.split("Значение ")[1]))
            else:
                question_list_final.append(question_word)
        self.clarifying_question = question_list_final

    def add_intent_in_list(self, intent):
        if self.available_intents_list is None:
            self.available_intents_list = [intent]
        else:
            self.available_intents_list.append(intent)

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

    def get_testing_pretty(self):
        res = {}
        res["name"] = self.name
        res["height"] = self.height
        return res

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

    def get_testing_pretty_children(self, all_scenes):
        print(all_scenes)
        child_counter = 0
        while child_counter < len(self.children) / 2:
            self.children[child_counter].get_testing_pretty_children(all_scenes)
            print(all_scenes)
            child_counter += 1
        all_scenes.append(self.get_testing_pretty())
        print(all_scenes)
        while child_counter < len(self.children):
            self.children[child_counter].get_testing_pretty_children(all_scenes)
            child_counter += 1
            print(all_scenes)
        return all_scenes

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
                        answer += ' ' + str(intent.get("intent"))
            elif isinstance(ans, IntentValue):
                for intent in intents_dicts:
                    if intent.get("intent") == ans.name:
                        answer += ' ' + str(intent.get("meaning"))
            else:
                answer += " " + ans

        return answer

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
    def pass_to_children(self, key_words):
        key_words.sort()
        pass_count = 0
        for pass_cond in self.pass_conditions:
            pass_count += 1
            checklist = []
            for int in pass_cond:
                if int in key_words:
                    checklist.append(int)
            # оставлены только уникальные интенты
            checklist = list(set(checklist))
            checklist.sort()
            print(checklist)
            print(key_words)
            # Переход в потомка с соответствующим номером
            if checklist == key_words and checklist != []:
                print(self.children)
                if self.children == []:
                    return self.name
                else:
                    return self.children[pass_count - 1].name
        for child in self.children:
            return child.pass_to_children(key_words)

    def count_descendants(self, counter, descendant_list):
        if self.children is not None:
            for child in self.children:
                counter += 1
                descendant_list.append(child)
        return counter, descendant_list

    # проверка входа в сцену, необходимо совпадение только по интентам, а не значениям
    def check_to_enter(self, only_intents):
        if set(self.available_intents_list) <= set(only_intents):
            return True


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

    def get_testing_pretty_nodes(self):
        all_scenes = []
        print(all_scenes)
        self.root.get_testing_pretty_children(all_scenes)
        print(all_scenes)
        return all_scenes

    def get_pretty_nodes(self):
        all_scenes = ""
        all_scenes += self.root.get_pretty_children(all_scenes)
        return all_scenes

    def get_final_nodes(self):
        all_scenes += self.root.get_pretty_children(all_scenes)

    def scene_add(self, parent_scene, name = None, children = None,
                  pass_conditions = None, answer = None, questions = None,
                  clarifying_question = None):
        new_scene = Scene(name = name, children = children,
                          pass_conditions = pass_conditions, answer = answer,
                          questions = questions,
                          clarifying_question = clarifying_question)

        parent_scene.add_child(new_scene)
        return new_scene

    def find_scene(self, intents):
        self.root.check_scene_rec(intents)

    def get_scenes_list(self):
        counter, scenes_list = self.root.count_descendants(0, [self.root])
        return counter, scenes_list

    # новый переход по сценам, параметр - найденные из речи интенты, graphnode
    def final_pass_to_scene(self, only_intents):
        # проверить принадлежность сцене, затем проверить принадлежность ее потомкам
        current_scene = self.root
        if not (current_scene.check_to_enter(only_intents)):
            return False
        starter = True
        while starter:
            starter = False
            if current_scene.check_to_enter(only_intents):
                for child in current_scene.children:
                    if child.check_to_enter(only_intents):
                        current_scene = child
                        starter = True
        return current_scene



def main():
    # Десериализация pickle
    #with open("save_files/pickle_test.PKL", "rb") as f:
     #    tree = pc.load(f)

    '''
    main_scene = Scene(name = "срок_приема_подготовки",
                       answer=["Да"],
                       pass_conditions=[["приём"]],
                       questions=[[IntentTemplate("срок"),
                                IntentTemplate("приём")]],
                       clarifying_question=["Не найден ответ в main"])
    sub1 = Scene(name="срок_приема_за_месяц", pass_conditions=[["месяц"]],
                 answer=["Да"],
                 questions=[[IntentTemplate("месяц")]])
    sub11 = Scene(name="прием_месяц", pass_conditions=[["приём", "срок"]],
                  answer=[IntentTemplate("срок"),
                          IntentValue("срок")],
                  questions=[[
                      "Какой",
                      IntentTemplate("приём"),
                      IntentValue("месяц")
                  ]])


    main_scene.add_child(sub1)
    sub1.add_child(sub11)
    tree = SceneTree(main_scene)
    tree.set_height_tree()
    '''

    main_scene = Scene(name="проверка_направлений",
                       answer=[IntentValue("балл")],
                       questions=[IntentTemplate("балл")],
                       available_intents_list=['балл'],
                       clarifying_question=["Не найден ответ в main"])
    sub1 = Scene(name="проверка_балла_направления", pass_conditions=["месяц"],
                 answer= [IntentTemplate("балл"),
                          IntentValue("балл"), IntentTemplate("направление"),
                          IntentValue("направление")],
                 available_intents_list=['направление', 'балл'],
                 questions=[IntentTemplate("балл"), IntentTemplate("направление")]
                 )
    tree = SceneTree(main_scene)
    main_scene.add_child(sub1)
    tree.set_height_tree()



    # Сериализация pickle
    with open("save_files/pickle_test.PKL", "wb") as f:
        pc.dump(tree, f)
    # # Сериализация pickle
    # with open("save_files/pickle_test.PKL", "wb") as f:
    #     pc.dump(tree, f)

    return tree


def get_scenes(dialog_tree):
    res = []
    get_scene(dialog_tree.root, res)
    return res


def get_scene(node, res):
    res.append(node)
    for child in node.children:
        get_scene(child, res)


def get_text_scenes(dialog_tree):
    return dialog_tree.get_pretty_nodes()


def get_testing_text_scenes(dialog_tree):
    return dialog_tree.get_testing_pretty_nodes()


def get_final_text_scenes(dialog_tree):
    return dialog_tree.get_final_nodes()

def get_root(dialog_tree):
    return dialog_tree.root


def get_scene_name(cur_scene):
    return cur_scene.name


def find_scene_by_name(name, dialog_tree):
    return dialog_tree.to_scene(name)


def get_scene_everything(current_scene):
    # Потомки
    children_return = []
    children = current_scene.children
    if children is not None:
        for child in children:
            children_return.append(child.name)
    else:
        children_return = None
    # Переходы
    pass_conditions_return = current_scene.pass_conditions
    # Ответ
    answer = current_scene.answer
    answer_return = []
    if answer is not None:
        for word in answer:
            if isinstance(word, IntentTemplate):
                answer_return.append("Шаблон интента: " + str(word.name))
            elif isinstance(word, IntentValue):
                answer_return.append(
                    "Шаблон значения интента: " + str(word.name))
            else:
                answer_return.append(word)
    else:
        answer_return = None
    # Вопросы
    questions = current_scene.questions
    questions_return = []
    if questions is not None:
        for question in questions:
            question_normal = []
            for word in question:
                if isinstance(word, IntentTemplate):
                    question_normal.append("Шаблон интента: " + str(word.name))
                elif isinstance(word, IntentValue):
                    question_normal.append(
                        "Шаблон значения интента: " + str(word.name))
                else:
                    question_normal.append(word)
            questions_return.append(question_normal)
    else:
        questions_return = None
    # Уточняющий вопрос
    clarifying_question = current_scene.clarifying_question
    clarifying_question_return = []
    if clarifying_question is not None:
        for word in clarifying_question:
            if isinstance(word, IntentTemplate):
                clarifying_question_return.append(
                    "Шаблон интента: " + str(word.name))
            elif isinstance(word, IntentValue):
                clarifying_question_return.append(
                    "Шаблон значения интента: " + str(word.name))
            else:
                clarifying_question_return.append(word)
    else:
        clarifying_question_return = None

    stats = [
        children_return,
        pass_conditions_return,
        answer_return,
        questions_return,
        clarifying_question_return
    ]
    return stats


def add_child(current_scene, child_scene, dialog_tree):
    current_scene.add_child(child_scene)
    dialog_tree.set_height_tree()


def add_scene(name, parent, pass_conditions, answer, questions,
              clarifying_question, dialog_tree):
    # Условия перехода пока одной строкой с разделением |
    pass_conditions_normal = []
    pass_condition = []
    pass_conditions_list = pass_conditions.split(' ')
    for word in pass_conditions_list:
        if word == "|":
            pass_conditions_normal.append(pass_condition)
            pass_condition = []
        else:
            pass_condition.append(word)
    pass_conditions_normal.append(pass_condition)

    # Шаблон ответа
    answer_list = answer.split(" ")
    answer_normal = []
    next_intent = False
    next_value = False
    for word in answer_list:
        if next_intent:
            answer_normal.append(IntentTemplate(word))
            next_intent = False
        elif next_value:
            answer_normal.append(IntentValue(word))
            next_value = False
        else:
            if word == "IT":
                next_intent = True
            elif word == "IV":
                next_value = True
            else:
                answer_normal.append(word)

    # Вопросы - аналогично условиям перехода, IT - следующее слово будет...
    # объектом интента, IV - аналогично значение
    questions_normal = []
    question = []
    questions_list = questions.split(" ")
    next_intent = False
    next_value = False
    for word in questions_list:
        if next_intent:
            question.append(IntentTemplate(word))
            next_intent = False
        elif next_value:
            question.append(IntentValue(word))
            next_value = False
        else:
            if word == "|":
                questions_normal.append(question)
                question = []
            elif word == "IT":
                next_intent = True
            elif word == "IV":
                next_value = True
            else:
                question.append(word)
    questions_normal.append(question)

    # Уточняющий вопрос
    clarifying_question_list = clarifying_question.split(" ")
    clarifying_question_normal = []
    next_intent = False
    next_value = False
    for word in clarifying_question_list:
        if next_intent:
            clarifying_question_normal.append(IntentTemplate(word))
            next_intent = False
        elif next_value:
            clarifying_question_normal.append(IntentValue(word))
            next_value = False
        else:
            if word == "IT":
                next_intent = True
            elif word == "IV":
                next_value = True
            else:
                clarifying_question_normal.append(word)

    to_add = Scene(name=name, pass_conditions=pass_conditions_normal,
                   answer=answer_normal, questions=questions_normal,
                   clarifying_question=clarifying_question_normal)
    parent_scene = dialog_tree.to_scene(parent)
    parent_scene.add_child(to_add)
    dialog_tree.set_height_tree()

    return to_add


def save_tree(file, dialog_tree):
    with open(file, "wb") as f:
        pc.dump(dialog_tree, f)


def find_parent(current_scene, find_scene):
    if current_scene.children is not None:
        print(current_scene.name)
        for child in current_scene.children:
            if child == find_scene:
                return current_scene
            else:
                return find_parent(child, find_scene)


def delete_scene(scene_name, dialog_tree):
    scene = find_scene_by_name(scene_name, dialog_tree)
    parent = find_parent(current_scene=dialog_tree.root, find_scene=scene)
    if parent is not None:
        parent.children.remove(scene)


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
def ask_question(current_scene, question_text, graph):
    question_intent_dict = current_scene.get_work_question(question_text)
    send_log("question", question_text, question_intent_dict,
             current_scene.name)
    if question_intent_dict:
        print("question_intent_dict")
        print(question_intent_dict)
        question_intent_dict = graph.search(question_intent_dict)
        print("new_question_dict")
        print(question_intent_dict)
        answer = current_scene.give_answer(question_intent_dict)
    else:
        answer = ""
    to_return = [answer, question_intent_dict]
    return to_return


def intent_dict_to_list(intent_dict):
    intent_list = []
    if not intent_dict:
        intent_dict = []
    for intent in intent_dict:
        int_name = intent.get("intent")
        intent_list.append(int_name)
    return intent_list


# Переход к следующей сцене (возможен переход сразу через несколько)
def pass_scene(cur_scene, intent_list):
    new_scene_name = cur_scene.pass_to_children(intent_list)
    return new_scene_name


# Ответ, новая сцена, словарь интентов и значений, лист интентов
def dialog(current_scene, question_text, graph):
    answer_and_intents = ask_question(current_scene, question_text, graph)
    answer = answer_and_intents[0]
    question_intent_dict = answer_and_intents[1]
    #question_intent_dict = current_scene.get_work_question(question_text)
    send_log("answer", answer, False, current_scene.name)
    if question_intent_dict:
        question_intent_dict = graph.search(question_intent_dict)
    intent_list = intent_dict_to_list(question_intent_dict)
    # print(intent_list)
    new_scene_name = pass_scene(current_scene, intent_list)
    return [answer, new_scene_name, question_intent_dict, intent_list]

def new_dialog(question, graph, dialog_tree):
    graph_intents = graph.nodes_intent_text
    #question = 'направление подготовки за год c баллом 200'
    question_normal = make_words_normal(question)
    question_intents = find_intents(graph_intents, question_normal)
    # сцена с шаблоном ответа
    new_scene = dialog_tree.final_pass_to_scene(question_intents)
    scene_intents = []
    if new_scene:
        for intent in new_scene.questions:
            if type(intent) == IntentTemplate:
                scene_intents.append(intent.name)

    #print(new_scene)
    list_dict_intents = []
    question_references = []
    for intent in scene_intents:
        question_references.append(graph.get_reference_lemma(intent))

    for intent in question_references:
        list_dict_intents.append({'intent':intent, 'meaning': None, 'type': 'REPRESENT'}) # represent - представление
    print(list_dict_intents)
    print('в граф для возможных')
    list_dict_intents_possible = graph.search(list_dict_intents, flag=True) # flag - true, если без значений
    print(list_dict_intents_possible)
    print("list_dict_intents_possible")
    # найдены возможные значения, проверить в вопросе
    list_dict_intents_meaning_found = []
    for intent in list_dict_intents_possible:
        remaining_meaning = []
        if intent['meaning'] != None:
            for meaning in intent['meaning']:
                if meaning in question_normal:
                    remaining_meaning.append(meaning)
        if not remaining_meaning:
            remaining_meaning = None
        intent_dict = {'intent': intent['intent'], 'meaning': remaining_meaning, 'type': 'REPRESENT'}
        list_dict_intents_meaning_found.append(intent_dict)
    list_dict_intents_final = graph.search(list_dict_intents_meaning_found)
    answer = ''
    if new_scene:
        for word in new_scene.answer:
            if type(word) == IntentTemplate:
                answer += word.name
            if type(word) == IntentValue:
                for intent_from_dict in list_dict_intents_final:
                    if intent_from_dict['intent'] == graph.get_reference_lemma(word.name):
                        answer += str(intent_from_dict['meaning'])
            if isinstance(word, str):
                answer += intent
            answer += ' '
    print(new_scene.name)
    print(list_dict_intents_meaning_found)
    print([answer, new_scene.name, list_dict_intents_final, scene_intents])
    send_log("answer", answer, False, new_scene.name)
    return [answer, new_scene.name, list_dict_intents_final, scene_intents]

# поиск интентов в вопросе по интентам графа
def find_intents(all_intents_text, question_text):
    question_intents = []
    for intent in all_intents_text:
        if intent in question_text:
            question_intents.append(intent)
    return question_intents


def make_words_normal(question):
    question_list = question.split(' ')
    normal_list = []
    for word in question_list:
        normal_list.append(morph.parse(word)[0].normal_form)
    normal_question = ' '.join(normal_list)
    return normal_question