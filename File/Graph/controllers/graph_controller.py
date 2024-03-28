from flask import current_app, request, jsonify, make_response, render_template
import pandas as pd
from werkzeug.utils import secure_filename
import os

document = None


def add(app, graph):
    @app.route('/graph/process_data', methods=['POST'])
    def process_data():
        global document
        document, clusters = graph.process_data(request.data.decode('utf-8'))
        return make_response(clusters.to_json(), 200)

    @app.route('/graph/load_data', methods=['POST'])
    def load_data():
        global document
        graph.load_data(document, parsing_json(request.json))
        return make_response('', 200)

    @app.route('/graph/delete_data', methods=['POST'])
    def delete_data():
        graph.delete_data(request.data.decode('utf-8'))
        graph.remove_document(request.data.decode('utf-8'))
        return make_response('', 200)  # 400

    @app.route('/graph/visible_data')
    def visible_data():
        graph.visible()
        return make_response('', 200)

    @app.route("/graph/update_document")
    def handle_get_documents():
        return make_response(get_documents(), 200)

    @app.route("/graph/update_reference")
    def handle_get_reference():
        return make_response(graph.get_documents(), 200)

    @app.route("/graph/upload_document", methods=["POST"])
    def handle_upload_document():
        rst = upload_document()
        return make_response(jsonify({'message': rst[0]}), rst[1])

    @app.route("/graph/test")
    def test():
        req = [{
            "intent": "подготовка", "meaning": ["прикладной математика информатика"]
        }, {
            "intent": "балл", "meaning": None
        }, {
            "intent": "год", "meaning": ["2020", "2022"]
        }]
        return graph.search(req)


def upload_document():
    if "file" not in request.files:
        return "Файл не найден", 400
    file = request.files["file"]
    if file.filename == "":
        return "Файл не выбран", 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER_DOCUMENTS"], filename))
        return "Файл успешно загружен", 200


def get_documents():
    return os.listdir(current_app.config["UPLOAD_FOLDER_DOCUMENTS"])


def parsing_json(json_data):
    df = pd.DataFrame(columns=[
        'index', 'layer', 'text', 'lemma', 'pos', 'con_index', 'con_dep', 'f_type', 'f_intent', 'f_value'
    ])
    for row in json_data['table']:
        values = [v.split(',') for v in row.values()]
        data = {
            'index':     [int(val) for val in values[0]],
            'layer':     int(values[1][0]),
            'text':      [val for val in values[2]],
            'lemma':     [val for val in values[3]],
            'pos':       [val for val in values[4]],
            'con_index': int(values[5][0]) if values[5][0] else None,
            'con_dep':   values[6][0],
            'f_type':    values[7][0],
            'f_intent':  values[8][0] == 'true',
            'f_value':   values[9][0] == 'true'
        }
        df = df._append(data, ignore_index=True)
    return df
