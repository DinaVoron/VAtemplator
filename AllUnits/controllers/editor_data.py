from app import app, graph, dialog_tree
from flask import render_template, request
from models.editor_data_model import get_ok_num, get_err_num, get_nf_num
from models.editor_data_model import count_errors, get_time, graph_verify
from models.dialog_model import get_testing_text_scenes
import subprocess


@app.route("/data", methods=["get", "post"])
def editor_data():

    start_date = ""
    end_date = ""

    ok_log = get_ok_num()
    err_log = get_err_num()
    nf_log = get_nf_num()

    all_log = ok_log + err_log + nf_log

    all_scenes = get_testing_text_scenes(dialog_tree=dialog_tree)

    if request.values.get("start_date") is not None:
        start_date = request.values.get("start_date")
    if request.values.get("end_date") is not None:
        end_date = request.values.get("end_date")

    if request.values.get("open_ok"):
        subprocess.Popen(["notepad", "logs/OK.log"])

    if request.values.get("open_err"):
        subprocess.Popen(["notepad", "logs/ERR.log"])

    if request.values.get("open_nf"):
        subprocess.Popen(["notepad", "logs/NF.log"])

    time = get_time(start_date, end_date)
    errs_per_scene = count_errors(start_date, end_date, dialog_tree)

    html = render_template(
        "editor_data.html",
        success_amount=ok_log,
        not_found_amount=nf_log,
        error_amount=err_log,
        all_amount=ok_log + nf_log + err_log,
        current_page="editor_data",
        errs_per_scene=errs_per_scene,
        time=time,
        start_date=start_date,
        end_date=end_date,
        all_scenes=all_scenes,
        len=len,
        int=int
    )
    return html
