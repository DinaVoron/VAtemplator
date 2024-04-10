from app import app, graph, dialog_tree
from flask import render_template, request
from models.dialog_model import (get_text_scenes, get_root, get_scene_name,
                                 find_scene_by_name, get_scene_everything,
                                 add_child, save_tree, add_scene)


@app.route("/", methods=["get", "post"])
def editor_tree():
    all_scenes = get_text_scenes(dialog_tree = dialog_tree)
    text_scenes = all_scenes.split('\n')
    # Если сцена не выбрана
    if request.values.get("go_to_scene"):
        scene_name = (request.values.get("scene_name"))
        current_scene = find_scene_by_name(scene_name,
                                           dialog_tree = dialog_tree)
        if current_scene is None:
            scene_name = None
            scene_stats = None
        else:
            scene_stats = get_scene_everything(current_scene)
    else:
        current_scene = get_root(dialog_tree=dialog_tree)
        scene_name = get_scene_name(current_scene)
        scene_stats = get_scene_everything(current_scene)

    if request.values.get("add_child_scene"):
        child_scene_name = (request.values.get("child_scene_name"))
        child_scene = find_scene_by_name(child_scene_name,
                                         dialog_tree = dialog_tree)
        if child_scene is None:
            child_scene_name = None
        else:
            add_child(current_scene, child_scene, dialog_tree = dialog_tree)
    else:
        child_scene_name = None

    if request.values.get("add_scene"):
        add_name = request.values.get("scene_name")
        add_parent = request.values.get("parent_scene_name")
        add_pass = request.values.get("pass_conditions")
        add_answer = request.values.get("answer")
        add_questions = request.values.get("questions")
        add_clarifying_question = request.values.get("clarifying_question")
        add_scene(name = add_name, parent = add_parent,
                  pass_conditions = add_pass,
                  answer = add_answer,
                  questions = add_questions,
                  clarifying_question = add_clarifying_question
                  )

    if request.values.get("save_tree"):
        save_tree("save_files/pickle_test.PKL", dialog_tree = dialog_tree)

    html = render_template(
        "editor_tree.html",
        current_page='editor_tree',

        text_scenes = text_scenes,
        current_scene = current_scene,
        scene_name = scene_name,
        scene_stats = scene_stats,
        child_scene_name = child_scene_name
    )
    return html
