import os
import pandas as pd
import spacy
import networkx as nx
from pyvis.network import Network
from models.module.graph_element import GraphNode, GraphEdge
from models.module.graph_nlp import ClusterType, create_clusters


class Graph:
    def __init__(self, documents_folder="./documents",
                 model="ru_core_news_lg"):
        """
        Конструктор класса Graph.

        Parameters:
        - documents_folder (str): Путь к папке с документами.
        - model (str): Модель для обработки естественного языка.
        """
        self.graph = nx.DiGraph()  # Инициализация направленного графа
        self.static_index = 1  # Статический индекс слова
        self.static_layer = 1  # Статический уровень предложения

        self.nlp = spacy.load(model)  # Загрузка модели
        self.documents = []  # Список документов
        self.documents_folder = documents_folder  # Путь к папке с документами

    def visible(self):
        """
        Функция для визуализации графа.

        Описание:
        - Создает объект сети для визуализации графа.
        - Добавляет узлы и рёбра графа в сеть с соответствующими параметрами.
        - Определяет форму, цвет и размер узлов в зависимости от типа узла.
        - Визуализирует граф и сохраняет его в HTML файл.
        """
        # Определение параметров узлов
        shape = ["triangle", "dot", "dot", "box"]
        color = ["#ffdd00", "#0055cc", "#00aacc", "#7a6a59"]
        size = [20, 12, 12, 10]

        # Создание объекта сети
        net = Network(
            width="100%", height="800px",
            bgcolor="#222222", font_color="white",
            notebook=False, directed=True,
            select_menu=False, filter_menu=True
        )
        # Установка параметров визуализации
        net.set_options(
            """const options = {
              "interaction": {
                "navigationButtons": true
              }
            }"""
        )

        # Добавление узлов в граф
        for i in self.graph.nodes:
            node = self.graph.nodes[i]

            # Определение формы, цвета и размера узла в зависимости от его типа
            if node["data"].is_intent and not node["data"].is_meaning:
                self.visible_node(net, i, node, shape[0], color[0], size[0])
                continue
            if node["data"].is_intent and node["data"].is_meaning:
                self.visible_node(net, i, node, shape[1], color[1], size[1])
                continue
            if not node["data"].is_intent and node["data"].is_meaning:
                self.visible_node(net, i, node, shape[2], color[2], size[2])
                continue
            if not node["data"].is_intent and not node["data"].is_meaning:
                self.visible_node(net, i, node, shape[3], color[3], size[3])
                continue

        # Добавление рёбер в граф
        for it in self.graph.edges:
            edge = self.graph.edges[it[0], it[1]]
            self.visible_edge(net, it, edge)

        # Сохранение графа в HTML-файл
        net.save_graph("static/graph.html")

    @staticmethod
    def visible_node(net, index, node, shape, color, size):
        """
        Добавляет узел в визуализацию графа.

        Parameters:
        - net (pyvis.network.Network): Объект сети для визуализации графа.
        - index (int): Индекс узла.
        - node (dict): Словарь, представляющий узел графа.
        - shape (str): Форма узла.
        - color (str): Цвет узла.
        - size (int): Размер узла.
        """
        title = f"""ID::{index}
                    > {node["data"].text}
                    > {node["data"].type}
                    Layer: #{str(node["layer"])[:50]}
        """
        net.add_node(
            index, label=" ".join(node["data"].text), title=title,
            layer=f"#{node['layer']}", shape=shape, color=color, size=size
        )

    @staticmethod
    def visible_edge(net, index, edge):
        """
        Добавляет ребро в визуализацию графа.

        Parameters:
        - net (pyvis.network.Network): Объект сети для визуализации графа.
        - index (tuple): Кортеж, представляющий индексы узлов, соединенных
        ребром.
        - edge (dict): Словарь, представляющий ребро графа.
        """
        title = f"""ID: {index[0]}::{index[1]}
                    > {edge["data"].text}
                    > {edge["data"].type}
        """
        if edge["data"].is_syntax:
            net.add_edge(index[0], index[1], title=title)
        if edge["data"].is_named:
            net.add_edge(index[0], index[1], title=title,
                         label=edge["data"].text)

    def search(self, request):
        """
        Функция для поиска информации в графе на основе запроса.

        Parameters:
        - request (list): Список запросов.

        Returns:
        - list: Обновленный список запросов с найденной информацией.
        """
        # Список для хранения слоев, связанных с запросом
        request_layer = []
        # Обработка каждого запроса
        for req in request:
            if (
                self.graph.has_node(req["intent"]) and
                self.graph.nodes[req["intent"]]["data"].is_intent
            ):
                intent = self.graph.nodes[req["intent"]]
                edges_in = list(self.graph.in_edges(req["intent"]))
                edges_out = list(self.graph.out_edges(req["intent"]))
                if req["meaning"] is not None:
                    layer = []
                    # Поиск слоев, связанных с указанным значением
                    for value in req["meaning"]:
                        for edge in edges_in:
                            node = self.graph.nodes[edge[0]]

                            if (
                                node["data"].is_meaning and
                                node["data"].is_text(value)
                            ):
                                layer += node["layer"]
                    request_layer.append(sorted(list(set(layer))))
            else:
                request_layer.append([])
                break
        # Находим общие слои для всех запросов
        if request_layer:
            request_layer = list(set(request_layer[0]).intersection(
                *request_layer[1:]))
        if not request_layer:
            return request
        # Обновляем запросы с найденной информацией
        for req in request:
            if req["meaning"] is None:
                intent = self.graph.nodes[req["intent"]]
                edges_in = list(self.graph.in_edges(req["intent"]))
                edges_out = list(self.graph.out_edges(req["intent"]))
                # Поиск значений
                for edge in edges_in:
                    node = self.graph.nodes[edge[0]]

                    if (
                        node["data"].is_meaning and
                        has_common_element(request_layer, node["layer"])
                    ):
                        if req["meaning"] is None:
                            req["meaning"] = [" ".join(node["data"].text)]
                        else:
                            req["meaning"].append(" ".join(node["data"].text))
        return request

    def process_data(self, document):
        """
        Функция для обработки данных из указанного документа.

        Parameters:
        - document (str): Имя документа.

        Returns:
        - tuple: Кортеж, содержащий имя документа и DataFrame с данными о кластерах.
        """
        # Создание DataFrame для хранения данных о кластерах
        df_clusters = pd.DataFrame(columns=[
            "index", "layer", "text", "lemma", "pos",
            "con_index", "con_dep", "f_type", "f_intent", "f_value"
        ])

        # Получение содержимого документа
        content = get_document_content(self.documents_folder, document)
        # Обработка содержимого документа с помощью обработки естественного языка
        doc = self.nlp(content)
        # Обход предложений в документе и создание кластеров
        for i, sent in enumerate(doc.sents):
            clusters, list_node = create_clusters(doc, sent)
            clusters = self.auto_allocation(clusters, list_node)
            # Добавление данных о кластерах в DataFrame
            df_clusters = pd.concat(
                [df_clusters, get_dataframe_clusters(i, clusters)],
                ignore_index=True
            )
        # Возвращение документа и DataFrame с данными о кластерах
        return document, df_clusters

    def load_data(self, document, data):
        doc = self.find_document(document)
        if doc:
            self.delete_data(document)
        else:
            self.create_document(document)
            doc = self.find_document(document)

        for i, row in data.iterrows():
            doc[1].add(self.static_layer + row["layer"])

            if row["f_intent"]:
                text = " ".join(row["lemma"])
                if self.graph.has_node(text):
                    if (
                        (self.static_layer + row["layer"]) not in
                        self.graph.nodes[text]["layer"]
                    ):
                        self.graph.nodes[text]["layer"] +=\
                            [self.static_layer + row["layer"]]
                else:
                    self.graph.add_node(
                        text,
                        data=GraphNode(row),
                        layer=[self.static_layer + row["layer"]]
                    )
                continue
            if row["f_value"]:
                self.graph.add_node(
                    self.static_index + i,
                    data=GraphNode(row),
                    layer=[self.static_layer + row["layer"]]
                )
                continue
            self.graph.add_node(
                self.static_index + i,
                data=GraphNode(row),
                layer=[self.static_layer + row["layer"]]
            )

        # ТРЕБУЕТСЯ ОПТИМИЗАЦИЯ :: СЛОЖНОСТЬ N^2
        for i, row in data.iterrows():
            for j, row_iter in data.iterrows():
                if (
                    row["con_index"] and i != j and
                    row["con_index"] in row_iter["index"]
                ):
                    if row["f_intent"]:
                        text = " ".join(row["lemma"])
                        if row_iter["f_intent"]:
                            text_iter = " ".join(row_iter["lemma"])
                            self.graph.add_edge(
                                text, text_iter,
                                data=GraphEdge(row["con_dep"],
                                               GraphEdge.TypeEdge.Syntax)
                                # layer=self.static_layer + row["layer"]
                            )
                            break
                        if row_iter["f_value"]:
                            self.graph.add_edge(
                                text, self.static_index + j,
                                data=GraphEdge(row["con_dep"],
                                               GraphEdge.TypeEdge.Syntax)
                                # layer=self.static_layer + row["layer"]
                            )
                            break
                        self.graph.add_edge(
                            text, self.static_index + j,
                            data=GraphEdge(row["con_dep"],
                                           GraphEdge.TypeEdge.Syntax)
                            # layer=self.static_layer + row["layer"]
                        )
                        break
                    if row["f_value"]:
                        if row_iter["f_intent"]:
                            text_iter = " ".join(row_iter["lemma"])
                            self.graph.add_edge(
                                self.static_index + i, text_iter,
                                data=GraphEdge(row["con_dep"],
                                               GraphEdge.TypeEdge.Syntax)
                                # layer=self.static_layer + row["layer"]
                            )
                            break
                        if row_iter["f_value"]:
                            self.graph.add_edge(
                                self.static_index + i, self.static_index + j,
                                data=GraphEdge(row["con_dep"],
                                               GraphEdge.TypeEdge.Syntax)
                                # layer=self.static_layer + row["layer"]
                            )
                            break
                        self.graph.add_edge(
                            self.static_index + i, self.static_index + j,
                            data=GraphEdge(row["con_dep"],
                                           GraphEdge.TypeEdge.Syntax)
                            # layer=self.static_layer + row["layer"]
                        )
                        break

                    if row_iter["f_intent"]:
                        text_iter = " ".join(row_iter["lemma"])
                        self.graph.add_edge(
                            self.static_index + i, text_iter,
                            data=GraphEdge(row["con_dep"],
                                           GraphEdge.TypeEdge.Syntax)
                            # layer=self.static_layer + row["layer"]
                        )
                        break
                    if row_iter["f_value"]:
                        self.graph.add_edge(
                            self.static_index + i, self.static_index + j,
                            data=GraphEdge(row["con_dep"],
                                           GraphEdge.TypeEdge.Syntax)
                            # layer=self.static_layer + row["layer"]
                        )
                        break
                    self.graph.add_edge(
                        self.static_index + i, self.static_index + j,
                        data=GraphEdge(row["con_dep"],
                                       GraphEdge.TypeEdge.Syntax)
                        # layer=self.static_layer + row["layer"]
                    )
                    break

        self.static_index += data.shape[0]
        self.static_layer += max(doc[1]) - (min(doc[1]) - 1)

    def delete_data(self, document):
        """
        Функция для удаления данных, связанных с указанным документом.

        Parameters:
        - document (str): Имя документа.
        """
        # Поиск указанного документа
        doc = self.find_document(document)
        # Если документ найден
        if doc:
            nodes_to_remove = []

            # Обход узлов графа
            for i in self.graph.nodes:
                node = self.graph.nodes[i]
                # Удаление слоев, связанных с указанным документом
                layer = [lr for lr in node["layer"] if lr not in doc[1]]
                if layer:
                    node["layer"] = layer
                else:
                    nodes_to_remove.append(i)

            # Удаление узлов, которые не имеют уровней
            for node in nodes_to_remove:
                self.graph.remove_node(node)

    def find_errors(self):
        """
        Функция для нахождения ошибок, такие как пустые узлы, изолированные
        узлы и несуществующие рёбра.

        Returns:
        - dict: Словарь, содержащий списки идентификаторов узлов с различными
        ошибками.
        """
        # Список для хранения идентификаторов пустых узлов
        empty_nodes = []
        # Список для хранения идентификаторов изолированных узлов
        isolated_nodes = []
        # Список для хранения рёбер с несуществующими узлами
        nonexistent_edges = []

        # Проверка каждого узла в графе
        for node in self.graph.nodes(data=True):
            node_id, attributes = node

            # Проверяем, есть ли у узла атрибуты
            if not attributes:
                empty_nodes.append(node_id)

            # Проверяем, есть ли у узла рёбра
            if self.graph.degree(node_id) == 0:
                isolated_nodes.append(node_id)

        # Проверка каждого ребра в графе
        for edge in self.graph.edges():
            src, dest = edge

            # Проверяем, существуют ли узлы
            if src not in self.graph or dest not in self.graph:
                nonexistent_edges.append(edge)

        # Возвращаем словарь с найденными ошибками
        return {
            "empty_nodes": empty_nodes,  # Пустые узлы
            "isolated_nodes": isolated_nodes,  # Изолированные узлы
            "nonexistent_edges": nonexistent_edges  # Несуществующие рёбра
        }

    def create_document(self, document):
        """
        Функция для добавления записи о новом документе.

        Parameters:
        - document (str): Имя нового документа.
        """
        self.documents.append((document, set()))

    def remove_document(self, document):
        """
        Функция для удаления записи о документе.

        Parameters:
        - document (str): Имя документа для удаления.
        """
        for i, doc in enumerate(self.documents):
            if doc[0] == document:
                del self.documents[i]
                break

    def find_document(self, document):
        """
        Функция для поиска записи о документе.

        Parameters:
        - document (str): Имя документа для поиска.

        Returns:
        - tuple or None: Кортеж с информацией о документе, если он найден,
        иначе None.
        """
        for doc in self.documents:
            if doc[0] == document:
                return doc
        return None

    def get_documents(self, sort=True):
        data = [doc[0] for doc in self.documents]
        return sorted(data) if sort else data

    @staticmethod
    def auto_allocation(clusters, list_node):
        """
        Автоматическое выделение интентов и значений для каждого кластера.

        Parameters:
        - clusters (list): Список кластеров.
        - list_node (list): Список узлов.

        Returns:
        - list: Список автоматически выделенных кластеров.
        """
        for cluster in clusters:
            if cluster.f_type == ClusterType.PartOfSpeech:
                cluster.f_intent = True
                cluster.f_value = True
            if cluster.f_type == ClusterType.Number:
                cluster.f_intent = False
                cluster.f_value = True
            if cluster.f_type == ClusterType.NamedEntity:
                cluster.f_intent = True
                cluster.f_value = False
            if (
                cluster.f_type == ClusterType.TokenCluster or
                cluster.f_type == ClusterType.TokenClusterQuoted
            ):
                cluster.f_intent = True
                cluster.f_value = True
        return clusters

    @property
    def nodes(self):
        return self.graph.nodes

    @property
    def edges(self):
        return self.graph.edges

    @property
    def list_intent(self):
        return [self.graph.nodes[i]["data"] for i in self.graph.nodes
                if self.graph.nodes[i]["data"].is_intent]

    @property
    def list_meaning(self):
        return [self.graph.nodes[i]["data"] for i in self.graph.nodes
                if self.graph.nodes[i]["data"].is_meaning]

    @property
    def list_intent_text(self):
        return [
            " ".join(self.graph.nodes[i]["data"].text)
            for i in self.graph.nodes if self.graph.nodes[i]["data"].is_intent
        ]

    @property
    def list_meaning_text(self):
        return [
            " ".join(self.graph.nodes[i]["data"].text)
            for i in self.graph.nodes if self.graph.nodes[i]["data"].is_meaning
        ]

    def parsing_node(self, i):
        if self.graph.has_node(i):
            node = self.graph.nodes[i]
            return {"text": " ".join(node["data"].text),
                    "layer": node["layer"],
                    "type": node["data"].type,
                    "intent": node["data"].is_intent,
                    "meaning": node["data"].is_meaning}
        return None

    def parsing_edge(self, i, j):
        if self.graph.has_edge(i, j):
            edge = self.graph.edges[i, j]
            return {"text": edge["data"].text,
                    "layer": edge["layer"],
                    "type": edge["data"].type,
                    "syntax": edge["data"].is_syntax,
                    "named": edge["data"].is_named}
        return None


def get_document_content(documents_folder, document):
    """
    Функция для получения содержимого указанного документа.

    Parameters:
    - documents_folder (str): Путь к папке с документами.
    - document (str): Имя документа.

    Returns:
    - str: Содержимое документа.
    """
    document_path = os.path.join(documents_folder, document)
    if not os.path.isfile(document_path):
        return ""
    with open(document_path, "r", encoding="utf-8") as f:
        content = f.read()
        content = " ".join(line.strip() for line in content.split())
        return content


def get_dataframe_clusters(layer, clusters):
    """
    Функция для создания DataFrame из кластеров.

    Parameters:
    - layer (int): Уровень кластеров.
    - clusters (list): Список кластеров.

    Returns:
    - pd.DataFrame: DataFrame с данными о кластерах.
    """
    data = {
        "index": [], "layer": [], "text": [], "lemma": [], "pos": [],
        "con_index": [], "con_dep": [], "f_type": [], "f_intent": [],
        "f_value": []
    }
    for cluster in clusters:
        data["index"].append(cluster.index)
        data["layer"].append(layer)
        data["text"].append(cluster.text)
        data["lemma"].append(cluster.lemma)
        data["pos"].append(cluster.pos)
        data["con_index"].append(cluster.con_index)
        data["con_dep"].append(cluster.con_dep)
        data["f_type"].append(cluster.f_type.name)
        data["f_intent"].append(cluster.f_intent)
        data["f_value"].append(cluster.f_value)
    return pd.DataFrame(data)


def has_common_element(array1, array2):
    """
    Функция для проверки наличия общего элемента в двух массивах.

    Parameters:
    - array1 (list): Первый массив.
    - array2 (list): Второй массив.

    Returns:
    - bool: True, если есть общий элемент, иначе False.
    """
    for element in array1:
        if element in array2:
            return True
    return False
