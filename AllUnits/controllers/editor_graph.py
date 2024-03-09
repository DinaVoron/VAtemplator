from app import app, graph
from flask import render_template


@app.route('/graph', methods=['get', 'post'])
def editor_graph():

    html = render_template(
        'editor_graph.html'
    )
    return html
