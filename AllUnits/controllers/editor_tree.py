from app import app, graph, dialog_tree
from flask import render_template, request
from models.dialog_model import (get_text_scenes, get_root, get_scene_name,
                                 find_scene_by_name, get_scene_everything,
                                 add_child, save_tree, add_scene, delete_scene,
                                 find_intents, make_words_normal, Scene,
                                 new_dialog)
import json
import jsons


@app.route("/", methods=["get", "post"])
def editor_tree():
    #all_scenes = get_text_scenes(dialog_tree = dialog_tree)
    #text_scenes = all_scenes.split('\n')
    all_tree = dialog_tree
    scenes_count, scenes_list = dialog_tree.get_scenes_list()
    json_scenes_list = jsons.dump(scenes_list)
    json_scenes_list = jsons.load(json_scenes_list)

    # Если сцена не выбрана
    if request.values.get("go_to_scene"):
        scene_name = request.values.get("scene_name")
        current_scene = find_scene_by_name(scene_name,
                                           dialog_tree = dialog_tree)
        if current_scene is None:
            scene_name = None
            scene_stats = None
        else:
            scene_stats = get_scene_everything(current_scene)
    elif request.values.get("delete_scene"):
        scene_name = request.values.get("hidden_scene_name_delete")
        delete_scene(scene_name, dialog_tree)
        current_scene = get_root(dialog_tree=dialog_tree)
    else:
        current_scene = get_root(dialog_tree = dialog_tree)
        scene_name = get_scene_name(current_scene)
        #scene_stats = get_scene_everything(current_scene)

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

    if request.values.get("save_tree"):
        save_tree("save_files/pickle_test.PKL", dialog_tree = dialog_tree)

    if request.values.get("Добавить интент"):
        current_scene.add_intent_in_list(request.values.get("graph_intents"))

    graph_intents = graph.nodes_intent_text
    graph_full_intents = graph.nodes_intent

    # Изменение сцены
    if request.values.get("change_scene"):
        old_scene_name = request.values.get("hidden_scene_name")
        new_scene_name = request.values.get("scene_name")
        answer = request.values.get("answer")
        short_answer = request.values.get("short_answer")
        questions = request.values.get("questions")
        available_intents = request.values.get("available_intents")
        clarifying_question = request.values.get("clarifying_question")

        scene = dialog_tree.to_scene(old_scene_name)
        scene.set_answer(answer)
        scene.set_short_answer(short_answer)
        scene.set_question(questions)
        scene.available_intents_list = available_intents.split(",")
        scene.set_clarifying_question(clarifying_question)
        scene.name = new_scene_name

        scenes_count, scenes_list = dialog_tree.get_scenes_list()
        json_scenes_list = jsons.dump(scenes_list)
        json_scenes_list = jsons.load(json_scenes_list)

    # добавление сцены
    if request.values.get("add_scene"):
        parent_scene_name = request.values.get("scene_parent")
        scene_name = request.values.get("scene_name_new")
        answer = request.values.get("answer_new")
        short_answer = request.values.get("short_answer_new")
        questions = request.values.get("questions_new")
        available_intents = request.values.get("available_intents_new")
        clarifying_question = request.values.get("clarifying_question_new")

        scene = Scene(name=scene_name)
        parent_scene = dialog_tree.to_scene(parent_scene_name)
        scene.set_answer(answer)
        scene.set_short_answer(short_answer)
        scene.set_question(questions)
        scene.available_intents_list = available_intents.split(",")
        scene.set_clarifying_question(clarifying_question)
        parent_scene.add_child(scene)

        scenes_count, scenes_list = dialog_tree.get_scenes_list()
        json_scenes_list = jsons.dump(scenes_list)
        json_scenes_list = jsons.load(json_scenes_list)

    html = render_template(
        "editor_tree.html",
        current_page='editor_tree',
        dialog_tree = dialog_tree,
        #text_scenes = text_scenes,
        current_scene = current_scene,
        scene_name = scene_name,
        #scene_stats = scene_stats,
        child_scene_name = child_scene_name,

        graph_intents = graph_intents,
        json_scenes_list = json_scenes_list
    )
    return html
