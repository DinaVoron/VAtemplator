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
    results = []
    for i in range(len(question_arr)):
        answers.append("")
        user_questions.append("")
        results.append("")
    scenes = get_scenes()
    is_answer = False

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

    if request.values.get("ok_result") or request.values.get("err_result"):
        is_answer = True
        answers = []
        for i in range(len(user_questions)):
            answer = get_scene_answer(get_scene_by_name(
                dialog_tree.root,
                selected_scene
            ), user_questions[i])
            answers.append(answer)
        if request.values.get("ok_result"):
            result_num = int(request.values.get("ok_result"))
            results[result_num] = "ok"
        if request.values.get("err_result"):
            result_num = int(request.values.get("err_result"))
            results[result_num] = "err"

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

    if request.values.get("set_type"):
        session["type"] = request.values.get("set_type")

    if "type" not in session:
        html = render_template(
            "editor_testing.html",
        )
        return html

    if session["type"] == "manual":
        html = render_template(
            "editor_testing_manual.html",
            scenes=scenes,
            selected_scene=selected_scene,
            questions=question_arr,
            user_questions=user_questions,
            answers=answers,
            is_answer=is_answer,
            results=results,
            len=len
        )
        return html

    if session["type"] == "auto":
        if request.values.get("open_test"):
            subprocess.Popen(["notepad", "logs/test.log"])
            if "test_result" not in session:
                test_result = automatic_testing()
                session["test_result"] = test_result
            else:
                test_result = session["test_result"]
                session["test_result"] = test_result
        else:
            test_result = automatic_testing()
            session["test_result"] = test_result

        html = render_template(
            "editor_testing_auto.html",
            test_result=test_result
        )
        return html

    if session["type"] == "verify":
        html = render_template(
            "editor_testing_verify.html"
        )
        return html