from app import app, graph, dialog_tree
from flask import render_template, request, make_response, jsonify
from models.dialog_model import (get_text_scenes, get_root, get_scene_name,
                                 find_scene_by_name, get_scene_everything,
                                 add_child, take_command, pass_scene,
                                 intent_dict_to_list, ask_question, dialog)

from models.editor_data_model import send_res


@app.route("/dialog", methods=["get", "post"])
def editor_dialog():
    question_text = ""

    if request.values.get("write_question"):
        scene_name = request.values.get("prev_scene")
        current_scene = find_scene_by_name(scene_name,
                                           dialog_tree = dialog_tree)
        question_text = request.values.get("question")
        all_list = dialog(current_scene, question_text, graph)
        answer = all_list[0]
        scene_name = all_list[1]
        current_scene = find_scene_by_name(scene_name,
                                           dialog_tree = dialog_tree)
        if current_scene is None:
            scene_name = request.values.get("prev_scene")
            current_scene = find_scene_by_name(scene_name,
                                               dialog_tree = dialog_tree)

    else:
        current_scene = get_root(dialog_tree = dialog_tree)
        scene_name = get_scene_name(current_scene)
        answer = None

    if request.values.get("end_dialog"):
        end_dialog = 1
    else:
        end_dialog = None

    if request.values.get("rate_dialog"):
        rating = int(request.values.get("rate_dialog"))
        if rating == 1:
            send_res("OK")
            pass
        else:
            send_res("ERR")
            pass

    html = render_template(
        "editor_dialog.html",
        current_scene=current_scene,
        scene_name=scene_name,
        end_dialog=end_dialog,
        answer = answer,
        question_text = question_text,
    )
    return html

@app.route("/chat/voice")
def handle_chat_voice():
    text = take_command()
    return make_response(jsonify({"message": text}), 200)