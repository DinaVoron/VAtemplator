from app import app, graph
from flask import render_template

# import graph


@app.route('/', methods=['get', 'post'])
def editor_tree():

    print(graph.edges)

    html = render_template(
        'editor_tree.html'
    )
    return html
