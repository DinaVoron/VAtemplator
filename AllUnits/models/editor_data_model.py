import xml.etree.ElementTree as ET
import datetime
import pymorphy3
from datetime import date
import re

from models.module.func import has_common_element


def get_scenes(dialog_tree):
    res = []
    get_scene(dialog_tree.root, res)
    return res


def get_scene(node, res):
    res.append(node)
    for child in node.children:
        get_scene(child, res)


def get_ok_num():
    success_amount = len(ET.parse("logs/OK.log").getroot())
    return success_amount


def get_err_num():
    error_amount = len(ET.parse("logs/ERR.log").getroot())
    return error_amount


def get_nf_num():
    not_found_amount = len(ET.parse("logs/NF.log").getroot())
    return not_found_amount


def count_errors(start_date, end_date, dialog_tree):
    res = {}
    scenes = get_scenes(dialog_tree)
    for scene in scenes:
        res[scene.name] = {}
        res[scene.name]['ok'] = 0
        res[scene.name]['err'] = 0
        res[scene.name]['nf'] = 0

    logs = ET.parse("logs/ERR.log").getroot()
    for log in logs:
        answers = log.findall("answer")
        for answer in answers:
            log_date = answer[0].text
            place = answer.find("place")
            if ((start_date == "" or start_date <= log_date)
                    and (end_date == "" or log_date <= end_date)):
                if place.text in res:
                    res[place.text]['err'] += 1

    logs = ET.parse("logs/OK.log").getroot()
    for log in logs:
        answers = log.findall("answer")
        for answer in answers:
            log_date = answer[0].text
            place = answer.find("place")
            if ((start_date == "" or start_date <= log_date)
                    and (end_date == "" or log_date <= end_date)):
                if place.text in res:
                    res[place.text]['ok'] += 1

    logs = ET.parse("logs/NF.log").getroot()
    for log in logs:
        questions = log.findall("question")
        for question in questions:
            log_date = question[0].text
            place = question.find("place")
            if ((start_date == "" or start_date <= log_date)
                    and (end_date == "" or log_date <= end_date)):
                if place.text in res:
                    res[place.text]['nf'] += 1
    for scene in res:
        all_scores = res[scene]['ok'] + res[scene]['err'] + res[scene]['nf']
        if all_scores == 0:
            res[scene]['color'] = 'var(--color_good_scene)'
        else:
            proportion = int(100 * (res[scene]['ok'] / all_scores))
            res[scene]['color'] = (
                    'color-mix(in oklab, var(--color_good_scene)'
                    + f' {proportion}%, var(--color_bad_scene))')
    return res


def get_time_one_log(logs, start_date, end_date, logs_amount):
    result_time = 0
    for log in logs:
        questions = log.findall("question")
        answers = log.findall("answer")
        i = 0
        while i < len(answers):
            log_date = answers[i][0].text
            start_time = datetime.datetime.strptime(
                questions[i][1].text,
                "%H:%M:%S"
            )
            end_time = datetime.datetime.strptime(
                answers[i][1].text,
                "%H:%M:%S"
            )
            if ((start_date == "" or start_date <= log_date)
                    and (end_date == "" or log_date <= end_date)):
                result_time += (end_time - start_time).seconds
                logs_amount[0] += 1
            else:
                i += 1
            i += 1
    return result_time


def get_time(start_date, end_date):
    time = 0
    amount = [0]
    logs = ET.parse("logs/OK.log").getroot()
    time += get_time_one_log(logs, start_date, end_date, amount)
    logs = ET.parse("logs/ERR.log").getroot()
    time += get_time_one_log(logs, start_date, end_date, amount)
    logs = ET.parse("logs/NF.log").getroot()
    time += get_time_one_log(logs, start_date, end_date, amount)
    if amount[0] == 0:
        return "0:00"
    result_time = round(time / amount[0], 2)
    print(result_time)
    return str(int(result_time)) + ":" + str(int((result_time % 1) * 100))


def one_layer(fir_node, sec_node):
    for fir_layer in fir_node.layer:
        for sec_layer in sec_node.layer:
            if fir_layer == sec_layer:
                return True
    return False


def find_all_paths(graph, current_node, visited, path, paths):
    visited[current_node] = True
    path.append(current_node)

    for neighbor in graph[current_node]:
        if neighbor in visited and not visited[neighbor]:
            find_all_paths(graph, neighbor, visited, path, paths)

    paths.append(path.copy())

    visited[current_node] = False
    path.pop()


def check_intent_tree(dialog_tree, paths):
    new_arr = []
    for i in range(len(paths)):
        if len(paths[i]) > 1:
            arr = []
            for j in range(len(paths[i])):
                arr.append(paths[i][j].text)
            if not dialog_tree.find_scene(arr):
                new_arr.append(arr)
    return new_arr


def find_all_chains(dialog_tree, edges):
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

    paths = check_intent_tree(dialog_tree, paths)

    return paths


def graph_verify(dialog_tree, graph):
    nodes = graph.nodes
    edges = []
    for i in nodes:
        for j in nodes:
            if i != j:
                if (nodes[i]['data'].is_intent
                        and not nodes[i]['data'].is_meaning
                        and nodes[j]['data'].is_intent
                        and not nodes[j]['data'].is_meaning):
                    if one_layer(nodes[i]['data'], nodes[j]['data']):
                        edges.append([nodes[i]['data'], nodes[j]['data']])
    chains = find_all_chains(dialog_tree, edges)

    tmp = []
    tmp_set = []
    for chain in chains:
        list_set = list(set(chain))
        if list_set not in tmp_set:
            tmp.append(chain)
            tmp_set.append(list_set)
    chains = tmp

    return chains


def send_log(rep_type, text, intent_values, place):
    f = open("logs/temp.log", "a+", encoding="utf-8")
    f.write(log_message_try(rep_type, text, intent_values, place) + "\r\n")


def log_message(text, intents_values_dic, place):
    if not intents_values_dic:
        intents_values_dic = []
    morph = pymorphy3.MorphAnalyzer()
    intent_values = intent_array(intents_values_dic)
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
            for intent in intent_values[words]:
                value_arr = str(intent).split(" ")
                print("value_arr")
                print(value_arr)
                arr_value_start = text_split_normal.index(
                    morph.parse(str(value_arr[0]))[0].normal_form
                )
                arr_value_end = text_split_normal.index(
                    morph.parse(str(
                        value_arr[len(value_arr) - 1]
                    ))[0].normal_form
                )
                text_split[arr_value_start] = ("<value>"
                                               + text_split[arr_value_start])
                text_split[arr_value_end] = (text_split[arr_value_end]
                                             + "</value>")

    res = "<text>" + " ".join(text_split) + "</text>"
    return ("<date>" + str(date.today()) + "</date>" + "<time>"
            + str(datetime.datetime.now().strftime("%H:%M:%S"))
            + "</time>" + res + "<place>" + place + "</place>")


def intent_array(intents_values):
    intent_values_new = {}
    if intents_values is not None:
        for i in range(len(intents_values)):
            intent_values_new[intents_values[i]["intent"]] = (
                intents_values)[i]["meaning"]
    return intent_values_new


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


def print_info(filename):
    f1 = open("logs/temp.log", "r+")
    f2 = open(filename, "r")
    text = f2.read()
    f2.close()
    text = re.sub("\\s*</?logs>\\s*", "", text)
    f2 = open(filename, "w")
    f2.write("<logs>\r\n" + text + "\r\n<log>\r\n" + f1.read()
             + "</log>\r\n"
             + "</logs>")
    f1.truncate(0)
    f1.close()
    f2.close()


def send_res(res):
    match res:
        case "OK":
            filename = "logs/OK.log"
            print_info(filename)
        case "ERR":
            filename = "logs/ERR.log"
            print_info(filename)
        case "NF":
            filename = "logs/NF.log"
            print_info(filename)


def log_message_try(rep_type, text, intents_values_dic, place):
    print("intents_values_dic")
    print(intents_values_dic)

    rep = ET.Element(rep_type)
    date_tree = ET.SubElement(rep, "date")
    date_tree.text = str(date.today())
    time = ET.SubElement(rep, "time")
    time.text = str(datetime.datetime.now().strftime("%H:%M:%S"))

    if not intents_values_dic:
        intents_values_dic = []
    morph = pymorphy3.MorphAnalyzer()
    intent_values = intent_array(intents_values_dic)
    text_split = multi_split(text)
    text_split_normal = []
    text_split_indexes = []

    for word in text_split:
        text_split_normal.append(morph.parse(word)[0].normal_form)
        text_split_indexes.append("")

    print("text_split_normal")
    print(text_split_normal)

    for words in intent_values:
        new_words = words.split(" ")
        if len(new_words) == 1:
            if new_words[0] in text_split_normal:
                arr_start_end = text_split_normal.index(new_words[0])
                text_split_indexes[arr_start_end] = "intent"
        else:
            if (new_words[0] in text_split_normal
                    and new_words[len(new_words) - 1] in text_split_normal):
                arr_start = text_split_normal.index(new_words[0])
                arr_end = text_split_normal.index(
                    new_words[len(new_words) - 1])
                text_split_indexes[arr_start] = "intent_start"
                text_split_indexes[arr_end] = "intent_end"

        if intent_values[words] is not None:
            for intent in intent_values[words]:
                value_arr = str(intent).split(" ")
                if len(value_arr) == 1:
                    if (morph.parse(str(value_arr[0]))[0].normal_form
                            in text_split_normal):
                        arr_value_start_end = text_split_normal.index(
                            morph.parse(str(value_arr[0]))[0].normal_form
                        )
                        text_split_indexes[arr_value_start_end] = "value"
                else:
                    if (morph.parse(str(value_arr[0]))[0].normal_form
                            in text_split_normal):
                        arr_value_start = text_split_normal.index(
                            morph.parse(str(value_arr[0]))[0].normal_form
                        )
                        arr_value_end = text_split_normal.index(
                            morph.parse(str(
                                value_arr[len(value_arr) - 1])
                            )[0].normal_form
                        )
                        text_split_indexes[arr_value_start] = "value_start"
                        text_split_indexes[arr_value_end] = "value_end"
    index = 0
    while index < len(text_split):
        text_arr = []
        if text_split_indexes[index] == "value_start":
            text_arr.append(text_split[index])
            last_index = index + 1
            while (last_index < len(text_split_indexes)
                   and text_split_indexes[last_index] != "value_end"):
                text_arr.append(text_split[last_index])
                last_index += 1
            text_arr.append(text_split[last_index])
            value = ET.SubElement(rep, "value")
            value.text = " ".join(text_arr)
            index = last_index + 1
            continue

        if text_split_indexes[index] == "value":
            value = ET.SubElement(rep, "value")
            value.text = text_split[index]
            index += 1
            continue

        if text_split_indexes[index] == "":
            text_arr.append(text_split[index])
            last_index = index + 1
            while (last_index < len(text_split_indexes)
                   and text_split_indexes[last_index] == ""):
                text_arr.append(text_split[last_index])
                last_index += 1
            text = ET.SubElement(rep, "text")
            text.text = " ".join(text_arr)
            index = last_index
            continue

        if text_split_indexes[index] == "intent":
            intent = ET.SubElement(rep, "intent")
            intent.text = text_split[index]
            index += 1
            continue

        if text_split_indexes[index] == "intent_start":
            text_arr.append(text_split[index])
            last_index = index + 1
            while (last_index < len(text_split_indexes)
                   and text_split_indexes[last_index] != "intent_end"):
                text_arr.append(text_split[last_index])
                last_index += 1
            text_arr.append(text_split[last_index])
            intent = ET.SubElement(rep, "intent")
            intent.text = " ".join(text_arr)
            index = last_index + 1
            continue

    place_tree = ET.SubElement(rep, "place")
    place_tree.text = place

    return bytes.decode(ET.tostring(rep, encoding='utf-8'))


def clean_logs():
    f1 = open("logs/temp.log", "r+")
    f1.truncate(0)
    f1.close()

# def get_scenes_names(dialog_tree):
#     return get_pretty_nodes(dialog_tree)
#
#
# def get_pretty_nodes(dialog_tree):
#     all_scenes = ""
#     all_scenes += get_pretty_children(dialog_tree.root, all_scenes)
#     return all_scenes
#
#
# def get_pretty_children(node, all_scenes):
#     child_counter = 0
#     while child_counter < len(node.children) / 2:
#         all_scenes = (node.children[child_counter].
#                       get_pretty_children(all_scenes))
#         child_counter += 1
#     all_scenes += node.get_pretty()
#     while child_counter < len(node.children):
#         all_scenes = (node.children[child_counter].
#                       get_pretty_children(all_scenes))
#         child_counter += 1
#     return all_scenes
