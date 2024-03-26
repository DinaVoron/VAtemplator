from flask import Flask, render_template
from models.graph_model import Graph
from tree import main


# Создание экземпляра объекта приложения
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Определение ключа

# Папка для загрузки файлов документов
app.config['UPLOAD_FOLDER_DOCUMENTS'] = 'documents'

# Определение глобальных статических переменных
graph = Graph()

dialog_tree = main()

import controllers.editor_tree
import controllers.editor_graph
import controllers.editor_testing
import controllers.editor_data


# if __name__ == '__main__':
#     app.run(debug=True)
