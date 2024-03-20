import xml.etree.ElementTree as ET
import datetime
from app import dialog_tree


def get_ok_num():
    success_amount = len(ET.parse("logs/OK.log").getroot())
    return success_amount


def get_err_num():
    error_amount = len(ET.parse("logs/ERR.log").getroot())
    return error_amount


def get_nf_num():
    not_found_amount = len(ET.parse("logs/NF.log").getroot())
    return not_found_amount


def count_errors():
    res = {}
    logs = ET.parse("logs/ERR.log").getroot()
    for log in logs:
        places = log.findall("place")
        for place in places:
            if place.text in res:
                res[place.text] += 0.5
            else:
                res[place.text] = 0.5
    return res


def get_time():
    time = 0
    amount = 0
    logs = ET.parse("logs/OK.log").getroot()
    for log in logs:
        times = log.findall('time')
        i = 1
        while i < len(times):
            time1 = datetime.datetime.strptime(
                times[i - 1].text,
                '%H:%M:%S'
            )
            time2 = datetime.datetime.strptime(
                times[i].text,
                '%H:%M:%S'
            )
            time += (time2 - time1).seconds
            amount += 1
            i += 2
    logs = ET.parse("logs/ERR.log").getroot()
    for log in logs:
        times = log.findall('time')
        i = 1
        while i < len(times):
            time1 = datetime.datetime.strptime(
                times[i - 1].text,
                '%H:%M:%S'
            )
            time2 = datetime.datetime.strptime(
                times[i].text,
                '%H:%M:%S'
            )
            time += (time2 - time1).seconds
            amount += 1
            i += 2
    logs = ET.parse("logs/NF.log").getroot()
    for log in logs:
        times = log.findall('time')
        i = 1
        while i < len(times):
            time1 = datetime.datetime.strptime(
                times[i - 1].text,
                '%H:%M:%S'
            )
            time2 = datetime.datetime.strptime(
                times[i].text,
                '%H:%M:%S'
            )
            time += (time2 - time1).seconds
            amount += 1
            i += 2
    return round(time/amount, 2)


def find_all_paths(graph, current_node, visited, path, paths):
    visited[current_node] = True
    path.append(current_node)

    for neighbor in graph[current_node]:
        if neighbor in visited and not visited[neighbor]:
            find_all_paths(graph, neighbor, visited, path, paths)

    paths.append(path.copy())

    visited[current_node] = False
    path.pop()


def check_intent_tree(paths):
    new_arr = []
    for i in range(len(paths)):
        if not dialog_tree.find_scene(paths[i]):
            new_arr.append(paths[i])
    return new_arr


def find_all_chains(edges, intents):
    print("intents")
    print(intents)
    graph = {}
    for edge in edges:
        if edge[0] not in graph and edge[0] in intents:
            graph[edge[0]] = []
        if edge[1] not in graph and edge[1] in intents:
            graph[edge[1]] = []

        if edge[0] in intents:
            graph[edge[0]].append(edge[1])
        if edge[1] in intents:
            graph[edge[1]].append(edge[0])

    visited = {node: False for node in graph}
    path = []
    paths = []

    for node in graph:
        find_all_paths(graph, node, visited, path, paths)

    paths = check_intent_tree(paths)

    return paths


def graph_verify(graph):
    print("Верификация графа...")
    nodes = graph.nodes
    edges = list(graph.edges)
    intents = graph.list_intent_text

    chains = find_all_chains(edges, intents)
    # for chain in chains:
    #     print(chain)
    return chains
