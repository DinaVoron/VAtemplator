from app import app, graph
from flask import render_template


@app.route('/data', methods=['get', 'post'])
def editor_data():

    html = render_template(
        'editor_data.html'
    )
    return html
