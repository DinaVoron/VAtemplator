import os
import spacy
from app import app, graph
from flask import current_app, jsonify, make_response, render_template, request
from werkzeug.utils import secure_filename
from models.module.func import create_html_content, create_html_cluster, has_common_element  # create_cluster_tr_html,

data = {}


# Определение страницы
# "Граф знаний / Семантическая сеть / Справочный граф"
@app.route("/graph", methods=["GET"])
def editor_graph():
    html = render_template(
        "editor_graph.html",
        current_page="editor_graph",
    )
    return html


# Определение основных запросов
# "Граф знаний / Семантическая сеть / Справочный граф"
@app.route("/graph/process_data", methods=["POST"])
def process_data():
    global data
    data_clear()

    data["name"]                  = request.data.decode("utf-8")
    data["doc"], data["clusters"] = graph.process_data(data["name"])

    return make_response(jsonify({
        "content_html":  create_html_content(graph, data),
        "clusters_html": create_html_cluster(graph, data)
    }), 200)


@app.route("/graph/process_data/draggable_cluster", methods=["POST"])
def __draggable_cluster__():
    global data
    index_list_src  = [int(index) for index in request.json.get("index_list_src")]
    index_list_dest = [int(index) for index in request.json.get("index_list_dest")]
    index = request.json.get("index")

    if draggable_cluster(index_list_src, index_list_dest, index):
        return jsonify({
            "flag": True,
            "content_html":  create_html_content(graph, data),
            "clusters_html": create_html_cluster(graph, data),
        })
    return jsonify({
        "flag": False
    })


@app.route("/graph/process_data/change_cluster_name", methods=["POST"])
def __change_cluster_name__():
    global data
    name_last = request.json.get('name_last')
    name_next = request.json.get('name_next')
    lemma = request.json.get('lemma')

    if graph.is_reference_name(name_last):
        pass
    else:
        if name_next not in data["reference"]:
            data["reference"][name_next] = set()
        data["reference"][name_next].add(lemma)
        data["reference"][name_last].remove(lemma)

    return make_response(jsonify({
        "content_html":  create_html_content(graph, data),
        "clusters_html": create_html_cluster(graph, data)
    }), 200)


@app.route("/graph/process_data/change_cluster_flag", methods=["POST"])
def __change_cluster_flag__():
    global data
    clusters = [data["clusters"][int(index)] for index in request.json.get('index_list')]

    if request.json.get('flag') == "intent":
        for cluster in clusters:
            if cluster.f_intent[1]:
                cluster.f_intent[0] = not cluster.f_intent[0]
    else:
        for cluster in clusters:
            if cluster.f_value[1]:
                cluster.f_value[0] = not cluster.f_value[0]
    return make_response(jsonify({
        "content_html":  create_html_content(graph, data),
        "clusters_html": create_html_cluster(graph, data)
    }), 200)


@app.route("/graph/process_data/select_cluster", methods=["POST"])
def __select_cluster__():
    global data
    index_list = [int(index) for index in request.json.get('index_list')]
    set_selection_status(index_list)

    return make_response(jsonify({
        "content_html":  create_html_content(graph, data),
        "clusters_html": create_html_cluster(graph, data)
    }), 200)


@app.route("/graph/load_data")
def load_data():
    global data
    name, clusters = data["name"], data["clusters"]
    data_clear()

    graph.load_data(name, clusters)
    return make_response("", 200)


@app.route("/graph/delete_data", methods=["POST"])
def delete_data():
    graph.delete_data(request.data.decode("utf-8"))
    return make_response("", 200)


# Определение вспомогательных запросов
# "Граф знаний / Семантическая сеть / Справочный граф"
@app.route("/graph/update_document")
def handle_update_document():
    documents = os.listdir(current_app.config["UPLOAD_FOLDER_DOCUMENTS"])
    return make_response(documents, 200)


@app.route("/graph/update_reference")
def handle_update_reference():
    return make_response(graph.get_documents(), 200)


@app.route("/graph/upload_document", methods=["POST"])
def handle_upload_document():
    rst = upload_document()
    return make_response(rst[0], rst[1])


@app.route("/graph/visible_data")
def visible_data():
    graph.visible()
    return make_response("", 200)


# Определение вспомогательных функций
def data_clear():
    global data
    data["name"]      = ""
    data["doc"]       = spacy.language.Language()
    data["clusters"]  = []
    data["proc_data"] = ([], [], [], [])
    data["reference"] = {}

    data["status"]                   = dict()
    data["status"]["select"]         = []
    data["status"]["select_related"] = []
    data["status"]["parent"]         = []
    data["status"]["child"]          = []


def set_selection_status(index_list):
    global data
    data["status"]["select"]         = []
    data["status"]["select_related"] = []
    data["status"]["parent"]         = []
    data["status"]["child"]          = []

    for index in index_list:
        if index == -1:
            continue
        cluster = data["clusters"][index]
        data["status"]["select"].append(cluster.index)

        for i, cluster_ in enumerate(data["clusters"]):
            if i in index_list:
                continue
            if cluster.p_name and cluster.p_name == cluster_.p_name:
                data["status"]["select_related"].append(cluster_.index)
                continue
            if has_common_element(cluster.connect_index, cluster_.index):
                data["status"]["parent"].append(cluster_.index)
                continue
            if has_common_element(cluster.index, cluster_.connect_index):
                data["status"]["child"].append(cluster_.index)
                continue


def draggable_cluster(index_list_src, index_list_dest, index):
    global data
    if __is_draggable_cluster__(index_list_src, index_list_dest, index):
        __draggable_cluster_union__(index_list_src, index_list_dest, index)
        return True
    return False


def __is_draggable_cluster__(index_list_src, index_list_dest, index):
    for index_src in index_list_src:
        cluster_src = data["clusters"][index_src]
        token = cluster_src.tokens[index]
        for index_dest in index_list_dest:
            cluster_dest = data["clusters"][index_dest]
            if token.index in cluster_dest.connect_index:
                return True
            if token.con_index in cluster_dest.index:
                return True
    return False


def __draggable_cluster_union__(index_list_src, index_list_dest, index):
    global data
    if data["status"]["select"]:
        index_list = []
        for i, cluster in enumerate(data["clusters"]):
            if cluster.index in data["status"]["select"]:
                index_list.append(i)
    else:
        index_list = []

    for index_src in index_list_src:
        cluster_src = data["clusters"][index_src]
        token = cluster_src.tokens[index]
        for index_dest in index_list_dest:
            cluster_dest = data["clusters"][index_dest]
            if token.index in cluster_dest.connect_index:
                cluster_src.remove(token)
                cluster_dest.insert(token)
                break
            if token.con_index in cluster_dest.index:
                cluster_src.remove(token)
                cluster_dest.insert(token)
                break

    if data["status"]["select"]:
        index_list_select = []
        step_empty        = 0
        for i, cluster in enumerate(data["clusters"]):
            if cluster.empty():
                for j, index_dest in enumerate(index_list_dest):
                    if index_dest == i - step_empty:
                        index_list_dest[j] = -1
                    elif index_dest > i - step_empty:
                        index_list_dest[j] -= 1
                step_empty += 1
                continue
            if i in index_list:
                index_list_select.append(i - step_empty)
    else:
        index_list_select = []

    data["clusters"] = list(filter(lambda cluster_: not cluster_.empty(), data["clusters"]))
    if data["status"]["select"]:
        if index_list_select:
            set_selection_status(index_list_select)
        else:
            set_selection_status(index_list_dest)


def upload_document():
    if "document" not in request.files:
        return "Файл не найден", 400
    file = request.files["document"]
    if file.filename == "":
        return "Файл не выбран", 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER_DOCUMENTS"], filename))
        return "Файл успешно загружен", 200
