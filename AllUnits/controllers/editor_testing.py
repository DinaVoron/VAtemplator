from app import app, graph, dialog_tree
from flask import render_template, request, session
from models.editor_testing_model import get_scenes, get_questions
from models.editor_testing_model import get_scene_by_name
from models.editor_testing_model import automatic_testing
from models.editor_testing_model import get_scene_answer
from models.editor_data_model import graph_verify
from fpdf import FPDF
import subprocess


def makePDF(scene_name, answers, user_questions):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font(
        "Sans",
        style="",
        fname="static/fonts/NotoSans-Medium.ttf",
        uni=True
    )
    pdf.set_font("Sans", size=12)
    pdf.set_fill_color(135, 206, 235)
    pdf.rect(0, 0, 220, 10, style="F")
    pdf.cell(
        190,
        0, txt="",
        ln=1,
        align="C"
    )
    pdf.cell(
        190,
        20, txt="Результаты автоматического тестирования",
        ln=1,
        border=1,
        align="C"
    )
    pdf.cell(
        190,
        20,
        txt="Тестируемая сцена: " + scene_name,
        ln=1,
        align="R"
    )
    for i in range(len(user_questions)):
        pdf.cell(
            200,
            10,
            txt=user_questions[i],
            ln=1
        )
        pdf.cell(
            200,
            10,
            txt=answers[i],
            ln=1
        )
    pdf.output("results.pdf")


@app.route("/testing", methods=["get", "post"])
def editor_testing():

    selected_scene = dialog_tree.root.name
    question_arr = get_questions(dialog_tree.root)
    answers = []
    user_questions = []
    results = []
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
            user_questions = []
        else:
            selected_scene = session["scene"]
            user_questions = request.values.getlist("questions")
    else:
        session["scene"] = dialog_tree.root.name

    if request.values.get("get_answers"):
        is_answer = True
        answers = []
        results = []
        for i in range(len(user_questions)):
            print("len(user_questions)")
            print(len(user_questions))
            answer = get_scene_answer(get_scene_by_name(
                dialog_tree.root,
                selected_scene
            ), user_questions[i])
            answers.append(answer)
            results.append("")

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

    if request.values.get("download_pdf"):
        is_answer = True
        answers = []
        for i in range(len(user_questions)):
            answer = get_scene_answer(get_scene_by_name(
                dialog_tree.root,
                selected_scene
            ), user_questions[i])
            answers.append(str(answer))
        makePDF(session["scene"], answers, user_questions)

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
            current_page='editor_testing',
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
            test_result=test_result,
            current_page='editor_testing'
        )
        return html

    if session["type"] == "verify":
        print("verify")
        intents = graph_verify(dialog_tree, graph)
        html = render_template(
            "editor_testing_verify.html",
            intents=intents,
            current_page='editor_testing',
            len=len
        )
        return html