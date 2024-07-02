from app import dialog_tree, graph
from models.dialog_model import IntentTemplate
from models.dialog_model import IntentValue
from models.dialog_model import find_scene_by_name, ask_question
from models.dialog_model import new_dialog
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
    intents = []
    values = []
    for value in node.questions:
        print(value)
        if isinstance(value, IntentTemplate):
            print("is_intent")
            intents.append("'" + value.name + "'")

        if isinstance(value, IntentValue):
            print("is_value")
            values.append("'" + value.name + "'")

    question_text = "c ключевыми словами " + ", ".join(intents)

    if len(values) > 0:
        question_text += " и значениями " + ", ".join(values)

    res.append(question_text)

    return res


def get_scene_by_name(node, name):
    print("Имена: ")
    print(node.name)
    print(name)
    if node.name == name:
        return node
    for child in node.children:
        scene = get_scene_by_name(child, name)
        if scene is not None:
            return scene
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
                    if elem.text is None:
                        question_text += " "
                    else:
                        question_text += elem.text + " "
            questions_arr.append(question_text)
        answers_tree = log.findall("answer")
        for answer in answers_tree:
            answer_text = ""
            for elem in answer:
                if elem.tag == "text":
                    if elem.text is None:
                        answer_text += ""
                    else:
                        answer_text += elem.text + " "
            answer_text = answer_text[0: len(answer_text) - 1]
            answers_arr.append(answer_text)

        answers.append(answers_arr)
        questions.append(questions_arr)


def automatic_testing():
    f1 = open("logs/test.log", "r+")
    f1.truncate(0)
    answers_arr = []
    question_arr = []
    # Получаем ответы и вопросы из файла успешного логирования
    log_tree = ET.parse("logs/OK.log", ET.XMLParser(encoding='utf-8'))
    get_ok(log_tree, answers_arr, question_arr)
    print(answers_arr)
    # Теперь получаем ответ на вопрос для каждого элемента массива, сравниваем
    input_answers = []
    for question_session in question_arr:
        scene = dialog_tree.root
        input_answers.append([])
        input_answers_end = len(input_answers) - 1
        for question in question_session:
            if scene is not None:
                dialog_all = new_dialog(question, graph, dialog_tree, [])
                answer = dialog_all[0]
                input_answers[input_answers_end].append(answer)
                scene = find_scene_by_name(dialog_all[1], dialog_tree)
            else:
                answer = "Не можем найти сцену..."
                input_answers[input_answers_end].append(answer)
                scene = None

    res = len(question_arr)
    q_len = len(question_arr)

    for i in range(len(answers_arr)):
        for j in range(len(answers_arr[i])):
            if answers_arr[i][j] != input_answers[i][j]:
                f1.write(question_arr[i][j] + "\r\n")
                f1.write("Правильный ответ:" + "\r\n")
                f1.write(answers_arr[i][j] + "\r\n")
                f1.write("Полученный ответ:" + "\r\n")
                f1.write(input_answers[i][j] + "\r\n")
                res -= 1
                break

    f1.close()
    return "Успешно пройдено {} из {} тестов!".format(res, q_len)


def get_scene_answer(scene, question):
    answer = scene.get_answer(question, graph)
    return answer


def pass_testing(root):
    res = []
    pass_testing_rec(res, root)


def pass_testing_rec(res, elem):
    for child in elem.children:
        pass_testing_rec(res, elem)


def pass_test():
    log_tree = ET.ElementTree.parse("logs/NF.log")
    for log in log_tree:
        print(log)
    return False
