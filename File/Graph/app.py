from flask import Flask, render_template
import controllers.graph_controller
from models.graph_model import Graph

# Создание экземпляра объекта приложения
app = Flask(__name__)

# Папка для загрузки файлов документов
app.config['UPLOAD_FOLDER_DOCUMENTS'] = 'documents'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template(
        'index.html'
    )


@app.route("/graph")
def graph_html():
    # Читаем содержимое HTML-файла
    with open('templates/graph.html', 'r') as file:
        html_content = file.read()

    # Возвращаем содержимое файла как ответ сервера
    return html_content


graph = Graph()

controllers.graph_controller.add(app, graph)

if __name__ == '__main__':
    app.run(debug=True)
