from app import app, graph
from flask import render_template, request
from models.editor_data_model import get_ok_num, get_err_num, get_nf_num
from models.editor_data_model import count_errors, get_time, graph_verify
import subprocess


@app.route('/data', methods=['get', 'post'])
def editor_data():
    success_amount = get_ok_num()
    not_found_amount = get_nf_num()
    error_amount = get_err_num()
    all_amount = success_amount + not_found_amount + error_amount

    errs_per_scene = count_errors()

    time = get_time()

    if request.values.get("open_ok"):
        subprocess.Popen(["notepad", "logs/OK.log"])

    if request.values.get("open_err"):
        subprocess.Popen(["notepad", "logs/ERR.log"])

    if request.values.get("open_nf"):
        subprocess.Popen(["notepad", "logs/NF.log"])

    intents = graph_verify(graph)

    html = render_template(
        'editor_data.html',
        success_amount=success_amount,
        not_found_amount=not_found_amount,
        error_amount=error_amount,
        all_amount=all_amount,
        errs_per_scene=errs_per_scene,
        intents=intents,
        time=time,
        len=len,
        int=int
    )
    return html
