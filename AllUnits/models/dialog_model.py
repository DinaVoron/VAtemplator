from app import dialog_tree
import tree
import pickle as pc
import speech_recognition as sr


def get_scenes():
    res = []
    get_scene(dialog_tree.root, res)
    return res


def get_scene(node, res):
    res.append(node)
    for child in node.children:
        get_scene(child, res)


def get_text_scenes():
    return dialog_tree.get_pretty_nodes()


def get_root():
    return dialog_tree.root

def get_scene_name(cur_scene):
    return cur_scene.name

def find_scene_by_name(name):
    return dialog_tree.to_scene(name)

def get_scene_everything(current_scene):
    stats = [
        current_scene.children,
        current_scene.pass_conditions,
        current_scene.answer,
        current_scene.questions
    ]
    return stats


def add_child(current_scene, child_scene):
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

    # Ответ - лист слов до ввода графа, todo: отделить интенты и значения от слов
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

    to_add = tree.Scene(name=name, pass_conditions=pass_conditions_normal, answer=answer, questions=questions_normal)
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