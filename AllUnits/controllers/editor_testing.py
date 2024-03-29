from app import app, graph, dialog_tree
from flask import render_template, request, session
from models.editor_testing_model import get_scenes, get_questions
from models.editor_testing_model import get_scene_by_name
from models.editor_testing_model import automatic_testing
from models.editor_testing_model import get_scene_answer


@app.route("/testing", methods=["get", "post"])
def editor_testing():

    selected_scene = dialog_tree.root.name
    question_arr = get_questions(dialog_tree.root)
    print(question_arr)
    answers = []
    for i in range(len(question_arr)):
        answers.append("")
    user_questions = []
    for i in range(len(question_arr)):
        user_questions.append("")
    scenes = get_scenes()
    is_test = False
    test_result = ""
    is_answer = False

    print(request.values.getlist("questions"))

    if 'scene' in session and session['scene'] is not None:
        print(0)
        if request.values.get("scene") is None:
            print(7)
            selected_scene = session['scene']
            print(session['scene'])
            question_arr = get_questions(dialog_tree.root)
            user_questions = request.values.getlist("questions")
            print(user_questions)
            answers = user_questions
            print(answers)
        elif session['scene'] != request.values.get("scene"):
            print(1)
            selected_scene = request.values.get("scene")
            question_arr = get_questions(get_scene_by_name(
                dialog_tree.root,
                selected_scene
            ))
            session['scene'] = selected_scene
        elif request.values.get("get_answers"):
            is_answer = True
            print(2)
            selected_scene = session['scene']
            print(selected_scene)
            print("getting answers...")
            question_arr = get_questions(get_scene_by_name(
                dialog_tree.root,
                selected_scene
            ))
            user_questions = request.values.getlist("questions")
            answers = []
            for i in range(len(user_questions)):
                answer = get_scene_answer(get_scene_by_name(
                    dialog_tree.root,
                    selected_scene
                ), user_questions[i])
                answers.append(answer)
            # answers = user_questions
            print(answers)
        else:
            print(3)
            selected_scene = session['scene']
            print(selected_scene)
            question_arr = get_questions(get_scene_by_name(
                dialog_tree.root,
                selected_scene
            ))
            print(question_arr)
            user_questions = request.values.getlist("questions")
            if request.values.get("test"):
                answers = []
                for i in range(len(user_questions)):
                    answer = get_scene_answer(get_scene_by_name(
                        dialog_tree.root,
                        selected_scene
                    ), user_questions[i])
                    answers.append(answer)
    else:
        print(4)
        # print("new scene...")
        session['scene'] = dialog_tree.root.name

    if request.values.get("test"):
        print("testing...")
        is_test = True
        test_result = automatic_testing()

    html = render_template(
        "editor_testing.html",
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
