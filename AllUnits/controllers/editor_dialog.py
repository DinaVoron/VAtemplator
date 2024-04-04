from app import app, graph
from flask import render_template, request, make_response, jsonify
from models.dialog_model import (get_text_scenes, get_root, get_scene_name,
                                 find_scene_by_name, get_scene_everything,
                                 add_child, take_command, pass_scene,
                                 intent_dict_to_list, ask_question, dialog)


@app.route('/dialog', methods=['get', 'post'])
def editor_dialog():
    all_scenes = get_text_scenes()
    text_scenes = all_scenes.split('\n')
    # Если сцена не выбрана
    if request.values.get('go_to_scene'):
        scene_name = (request.values.get('scene_name'))
        current_scene = find_scene_by_name(scene_name)
        if current_scene is None:
            scene_name = None
            scene_stats = None
        else:
            scene_stats = get_scene_everything(current_scene)
        answer = None
    elif request.values.get('write_question'):
        scene_name = request.values.get('prev_scene')
        current_scene = find_scene_by_name(scene_name)
        scene_stats = get_scene_everything(current_scene)
        question = request.values.get('question')
        all_list = dialog(current_scene, question)
        answer = all_list[0]
        scene_name = all_list[1]
        current_scene = find_scene_by_name(scene_name)

    else:
        current_scene = get_root()
        scene_name = get_scene_name(current_scene)
        scene_stats = get_scene_everything(current_scene)
        answer = None

    if request.values.get('end_dialog'):
        end_dialog = 1
    else:
        end_dialog = None

    if request.values.get('rate_dialog'):
        rating = request.values.get('rate_dialog')
        if (rating == 1):
            # Удовлетворительно
            pass
        else:
            # Неудовлетворительно
            pass

    html = render_template(
        'editor_dialog.html',
        text_scenes=text_scenes,
        current_scene=current_scene,
        scene_name=scene_name,
        scene_stats=scene_stats,
        end_dialog=end_dialog,
        answer = answer
    )
    return html

@app.route("/chat/voice")
def handle_chat_voice():
    text = take_command()
    return make_response(jsonify({'message': text}), 200)