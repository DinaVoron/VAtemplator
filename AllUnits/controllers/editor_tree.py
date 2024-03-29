from app import app, graph
from flask import render_template, request
from models.dialog_model import (get_text_scenes, get_root, get_scene_name,
                                 find_scene_by_name, get_scene_everything,
                                 add_child, save_tree, add_scene)


@app.route('/', methods=['get', 'post'])
def editor_tree():
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
    else:
        current_scene = get_root()
        scene_name = get_scene_name(current_scene)
        scene_stats = get_scene_everything(current_scene)

    if request.values.get('add_child_scene'):
        child_scene_name = (request.values.get('child_scene_name'))
        child_scene = find_scene_by_name(child_scene_name)
        if child_scene is None:
            child_scene_name = None
        else:
            add_child(current_scene, child_scene)
    else:
        child_scene_name = None

    if request.values.get('add_scene'):
        add_name = request.values.get('scene_name')
        add_parent = request.values.get('parent_scene_name')
        add_pass = request.values.get('pass_conditions')
        add_answer = request.values.get('answer')
        add_questions = request.values.get('questions')
        add_scene(name=add_name, parent=add_parent, pass_conditions=add_pass, answer=add_answer,
                  questions=add_questions)

    if request.values.get('save_tree'):
        save_tree("pickle_test.PKL")

    html = render_template(
        'editor_tree.html',
        text_scenes=text_scenes,
        current_scene=current_scene,
        scene_name=scene_name,
        scene_stats=scene_stats,
        child_scene_name=child_scene_name
    )
    return html
