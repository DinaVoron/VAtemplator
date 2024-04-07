from app import dialog_tree
from models.dialog_model import IntentTemplate
from models.dialog_model import IntentValue
import xml.etree.ElementTree as ET


def get_scenes():
    res = []
    get_scene(dialog_tree.root, res)
    return res


def get_scene(node, res):
    res.append(node)
    for child in node.children:
        get_scene(child, res)


def get_questions(node):
    if node is None:
        return []
    res = []
    for question in node.questions:
        intents = []
        values = []
        for item in question:
            if isinstance(item, IntentTemplate):
                intents.append(item.name)
            if isinstance(item, IntentValue):
                values.append(item.name)

        question_text = "c интентами " + ", ".join(intents)
        res.append(question_text)

    return res


def get_scene_by_name(node, name):
    if node.name == name:
        return node
    for child in node.children:
        return get_scene_by_name(child, name)
    return None


def get_ok(log_tree, answers, questions):
    root = log_tree.getroot()
    for log in root:
        answers_arr = []
        questions_arr = []
        questions_tree = log.findall("question")
        for question in questions_tree:
            question_text = ""
            for elem in question:
                if (elem.tag != "place"
                        and elem.tag != "time"
                        and elem.tag != "date"):
                    question_text += elem.text + " "
            questions_arr.append(question_text)
        answers_tree = log.findall("answer")
        for answer in answers_tree:
            answer_text = ""
            for elem in answer:
                if elem.tag == "text":
                    answer_text += elem.text + " "
            answers_arr.append(answer_text)

        answers.append(answers_arr)
        questions.append(questions_arr)


def automatic_testing():
    answers_arr = []
    question_arr = []
    # Получаем ответы и вопросы из файла успешного логирования
    log_tree = ET.parse("logs/OK.log")
    get_ok(log_tree, answers_arr, question_arr)
    # Теперь получаем ответ на вопрос для каждого элемента массива, сравниваем
    q_len = len(question_arr)
    res = q_len
    return "Успешно пройдено {} из {} тестов!".format(res, q_len)


def get_scene_answer(scene, question):
    answer = scene.get_work_question(question)
    return answer
