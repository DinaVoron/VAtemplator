import logging
import xml.etree.ElementTree as ET
from state import set_debug
import pymorphy3
morph = pymorphy3.MorphAnalyzer()

def send_log(text, intents_values, place):
    logging.basicConfig(
        filename="temp.log",
        encoding="utf-8",
        level=logging.INFO,
        force=True,
        format="%(asctime)s %(message)s",
        datefmt="%m-%d %H:%M:%S")
    logging.info(make_log_message(text, intents_values, place))


def intent_array(intents_values):
    intent_values_new = {}
    for i in range(len(intents_values)):
        intent_values_new[intents_values[i]["intent"]] = intents_values[i]["meaning"]
    return intent_values_new


def log_message(text, intents_values_dic, place):
    intent_values = intent_array(intents_values_dic)
    res = ""
    text_arr = []
    intent_arr = []
    text_split = text.split(" ")
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
    return res




def print_info(filename):
    f1 = open("temp.log", "r+")
    f2 = open(filename, "a+'")
    f2.write(f1.read())
    f2.write('--------\n')
    f1.truncate(0)
    f1.close()
    f2.close()


def send_res(res):
    match res:
        case "OK":
            filename = "OK.log"
            print_info(filename)
        case "ERR":
            filename = "ERR.log"
            print_info(filename)
        case "NF":
            filename = "NF.log"
            print_info(filename)


def get_text_question(elem, question):
    for child in elem:
        get_text_question(child, question)
        if child.text is not None and child.text.find('\n'):
            question[0] += child.text + " "


# функция, приводящая xml в вопрос
def get_question(filename):
    question = [""]
    tree = ET.parse(filename)
    root = tree.getroot()
    get_text_question(root, question)
    return question[0]


def get_ok(answers, questions):
    f1 = open("OK.log", "r")
    lines = f1.readlines()
    cur = 0
    while cur < len(lines):
        if lines[cur][0] == "-":
            cur += 1
            continue
        else:
            answers.append(lines[cur].split(" ")[2])
            cur += 1
            questions.append(lines[cur].split(" ")[2])
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
    print("Успешно пройдено {} из {} тестов!".format(res, q_len))
    return res


test_text = "Скажи средний балл по программной инженерии в 2020 году"
test_intents_values = [
    {"intent": "балл", "meaning": None},
    {"intent": "год", "meaning": 2020}
]
test_place = "2030ed"



# print(intent_array(test_intents_values))
print(log_message(test_text, test_intents_values, test_place))

