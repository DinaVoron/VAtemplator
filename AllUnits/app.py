from flask import Flask, session
from graph import init_graph, graph_nlp_text
from pickler import unpickle, topickle
from tree import SceneTree, Scene, IntentValue, IntentTemplate, main
import pickle as pc

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

text = """
Проходной балл по направлению подготовки "Прикладная математика и информатика" в 2020 году составил 197 баллов.
Проходной балл по направлению подготовки "Прикладная математика и информатика" в 2021 году составил 211 баллов.
Проходной балл по направлению подготовки "Прикладная математика и информатика" в 2022 году составил 200 баллов.
Проходной балл по направлению подготовки "Прикладная математика и информатика" в 2023 году составил 230 баллов.
В 2020 году по направлению подготовки "Математика и компьютерные науки" проходной балл равен 190.
В 2021 году по направлению подготовки "Математика и компьютерные науки" проходной балл равен 172.
В 2022 году по направлению подготовки "Математика и компьютерные науки" проходной балл равен 204.
В 2023 году по направлению подготовки "Математика и компьютерные науки" проходной балл равен 200.
"""
graph = init_graph()
graph = graph_nlp_text(graph, text)

dialog_tree = main()
#dialog_tree = unpickle("pickle_test.PKL")
#print(dialog_tree.print_pretty_nodes())



import controllers.editor_tree
import controllers.editor_graph
import controllers.editor_testing
import controllers.editor_data
import controllers.editor_dialog