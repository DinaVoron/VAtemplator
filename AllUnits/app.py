import os
from flask import Flask, session, render_template
from models.graph_model import Graph
#from tree import SceneTree, Scene, IntentValue, IntentTemplate, main
from models.dialog_model import SceneTree, Scene, IntentValue, IntentTemplate, main
# from tree import main
# import pickle as pc


# Создание экземпляра объекта приложения
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Определение ключа

# Папка для загрузки файлов документов
app.config['UPLOAD_FOLDER_DOCUMENTS'] = "documents"

# Определение глобальных статических переменных
if os.path.exists("save_files/graph.pkl"):
    graph = Graph.load("save_files/graph.pkl")
else:
    graph = Graph()

dialog_tree = main()


import controllers.editor_tree
import controllers.editor_graph
import controllers.editor_testing
import controllers.editor_data
import controllers.editor_dialog
