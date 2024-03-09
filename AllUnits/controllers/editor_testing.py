from app import app, graph
from flask import render_template


@app.route('/testing', methods=['get', 'post'])
def editor_testing():

    html = render_template(
        'editor_testing.html'
    )
    return html
