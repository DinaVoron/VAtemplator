from app import app, graph, dialog_tree
from flask import render_template, request
from models.editor_data_model import get_ok_num, get_err_num, get_nf_num
from models.editor_data_model import count_errors, get_time, graph_verify
import subprocess


@app.route("/data", methods=["get", "post"])
def editor_data():
    success_amount = get_ok_num()
    not_found_amount = get_nf_num()
    error_amount = get_err_num()
    all_amount = success_amount + not_found_amount + error_amount
    start_date = None
    end_date = None
    if request.values.get("start_date") != '':
        start_date = request.values.get("start_date")
    if request.values.get("end_date") != '':
        end_date = request.values.get("end_date")

    errs_per_scene = count_errors()

    if request.values.get("open_ok"):
        subprocess.Popen(["notepad", "logs/OK.log"])

    if request.values.get("open_err"):
        subprocess.Popen(["notepad", "logs/ERR.log"])

    if request.values.get("open_nf"):
        subprocess.Popen(["notepad", "logs/NF.log"])

    print("start_date")
    print(start_date)
    print("end_date")
    print(end_date)
    time = get_time(start_date, end_date)

    html = render_template(
        "editor_data.html",
        current_page='editor_data',
        success_amount=success_amount,
        not_found_amount=not_found_amount,
        error_amount=error_amount,
        all_amount=all_amount,
        errs_per_scene=errs_per_scene,
        time=time,
        len=len,
        int=int
    )
    return html
