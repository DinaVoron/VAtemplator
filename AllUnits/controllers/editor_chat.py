from app import app, graph, dialog_tree
from flask import render_template, request, make_response, jsonify
from models.dialog_model import get_root, get_scene_name, find_scene_by_name, dialog, new_dialog
from models.editor_data_model import send_res, clean_logs


@app.route("/chat", methods=["GET"])
def editor_chat():
    clean_logs()

    html = render_template(
        "editor_chat.html",
        current_page="editor_chat",

        scene_name=get_scene_name(get_root(dialog_tree=dialog_tree)),
        message="Приветствую! Я готов ответить на ваши вопросы."
    )
    return html


@app.route("/chat/send", methods=["POST"])
def handle_chat_send():
    current_scene            = find_scene_by_name(request.json.get("scene"), dialog_tree=dialog_tree)
    question                 = request.json.get("question")
    #answer, scene_name, _, _ = dialog(current_scene, question, graph)
    answer, scene_name, _, _ = new_dialog(question, graph, dialog_tree)

    if find_scene_by_name(scene_name, dialog_tree=dialog_tree) is None:
        scene_name = request.json.get("scene")
    if not answer:
        answer = "Мои соболезнования. Я не нашел ответа на ваш вопрос."

    return make_response(jsonify({
        "scene_name": scene_name, "question": question, "answer": answer,
    }), 200)


@app.route("/chat/rating", methods=["POST"])
def handle_chat_rating():
    send_res(str(request.data.decode("utf-8")))
    return make_response(jsonify({
        "scene_name": get_scene_name(get_root(dialog_tree=dialog_tree)), "message": "Приветствую! Я готов ответить на ваши вопросы."
    }), 200)

# from app import app, graph, dialog_tree
# from flask import render_template, request, make_response, jsonify
# from models.dialog_model import (get_text_scenes, get_root, get_scene_name,
#                                  find_scene_by_name, get_scene_everything,
#                                  add_child, take_command, pass_scene,
#                                  intent_dict_to_list, ask_question, dialog)
#
# from models.editor_data_model import send_res, clean_logs
#
#
# @app.route("/dialog", methods=["get", "post"])
# def editor_dialog():
#     question_text = ""
#
#     if len(request.args) == 0:
#         clean_logs()
#
#     if request.values.get("write_question"):
#         scene_name = request.values.get("prev_scene")
#         current_scene = find_scene_by_name(scene_name,
#                                            dialog_tree = dialog_tree)
#         question_text = request.values.get("question")
#         all_list = dialog(current_scene, question_text, graph)
#         answer = all_list[0]
#         scene_name = all_list[1]
#         current_scene = find_scene_by_name(scene_name,
#                                            dialog_tree = dialog_tree)
#         if current_scene is None:
#             scene_name = request.values.get("prev_scene")
#             current_scene = find_scene_by_name(scene_name,
#                                                dialog_tree = dialog_tree)
#
#     else:
#         current_scene = get_root(dialog_tree = dialog_tree)
#         scene_name = get_scene_name(current_scene)
#         answer = None
#
#     if request.values.get("end_dialog"):
#         end_dialog = 1
#     else:
#         end_dialog = None
#
#     if request.values.get("rate_dialog"):
#         rating = int(request.values.get("rate_dialog"))
#         if rating == 1:
#             send_res("OK")
#             pass
#         else:
#             send_res("ERR")
#             pass
#
#     html = render_template(
#         "editor_dialog.html",
#         current_page='editor_dialog',
#         current_scene=current_scene,
#         scene_name=scene_name,
#         end_dialog=end_dialog,
#         answer = answer,
#         question_text = question_text,
#     )
#     return html
#
# @app.route("/chat/voice")
# def handle_chat_voice():
#     text = take_command()
#     return make_response(jsonify({"message": text}), 200)
