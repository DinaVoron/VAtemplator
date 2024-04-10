from app import app, graph, dialog_tree
from flask import render_template, request, session
from models.editor_testing_model import get_scenes, get_questions
from models.editor_testing_model import get_scene_by_name
from models.editor_testing_model import automatic_testing
from models.editor_testing_model import get_scene_answer
import subprocess


@app.route("/testing", methods=["get", "post"])
def editor_testing():

    selected_scene = dialog_tree.root.name
    question_arr = get_questions(dialog_tree.root)
    answers = []
    user_questions = []
    for i in range(len(question_arr)):
        answers.append("")
        user_questions.append("")
    scenes = get_scenes()
    is_test = False
    test_result = ""
    is_answer = False

    if request.values.get("open_test"):
        subprocess.Popen(["notepad", "logs/test.log"])
        is_test = True

    if "scene" in session and session["scene"] is not None:
        if request.values.get("scene") is None:
            selected_scene = session["scene"]
        elif session["scene"] != request.values.get("scene"):
            selected_scene = request.values.get("scene")
            session["scene"] = selected_scene
        else:
            selected_scene = session["scene"]
        user_questions = request.values.getlist("questions")
    else:
        session["scene"] = dialog_tree.root.name

    if request.values.get("test"):
        is_test = True
        test_result = automatic_testing()

    if request.values.get("get_answers"):
        is_answer = True
        answers = []
        for i in range(len(user_questions)):
            answer = get_scene_answer(get_scene_by_name(
                dialog_tree.root,
                selected_scene
            ), user_questions[i])
            answers.append(answer)

    question_arr = get_questions(get_scene_by_name(
        dialog_tree.root,
        selected_scene
    ))

    html = render_template(
        "editor_testing.html",
        current_page='editor_testing',

        len=len,
        scenes=scenes,
        selected_scene=selected_scene,
        questions=question_arr,
        is_test=is_test,
        test_result=test_result,
        user_questions=user_questions,
        answers=answers,
        is_answer=is_answer
    )
    return html
