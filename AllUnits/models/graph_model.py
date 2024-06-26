import networkx as nx
import spacy
import pickle
from pyvis.network import Network
from models.module.func import get_document_content, has_common_element
from models.module.graph_element import GraphNode, GraphEdge
from models.module.graph_nlp import ClusterType, create_clusters


class Graph:
    def __init__(self, documents_folder="./documents", model="ru_core_news_lg"):
        """
        Конструктор класса Graph.

        Parameters:
        - documents_folder (str): Путь к папке с документами.
        - model (str): Модель для обработки естественного языка.
        """
        self.graph     = nx.DiGraph()
        self.documents = {}
        self.reference = {}

        self.nlp              = spacy.load(model)
        self.documents_folder = documents_folder
        self.static_index     = 1
        self.static_layer     = 1

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
        shape = ["triangle", "dot", "box"]
        color = ["#ffdd00", "#7109AA", "#009B95", "#7a6a59"]
        size  = [20, 12, 10]

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
            node = self.graph.nodes[i]["data"]

            if node.type == "Represent":
                self.visible_node(net, i, node, shape[0], color[0], size[0])
                continue

            if node.type[0] == "NodeInt":
                if node.type[1] == "Intent":
                    self.visible_node(net, i, node, shape[0], color[1], size[1])
                    continue
                if node.type[1] == "IntentAndMeaning":
                    self.visible_node(net, i, node, shape[0], color[2], size[1])
                    continue

            if node.type[0] == "NodeVal":
                if node.type[1] == "Meaning":
                    self.visible_node(net, i, node, shape[1], color[2], size[2])
                    continue
                if node.type[1] == "Null":
                    self.visible_node(net, i, node, shape[2], color[3], size[2])
                    continue

        # Добавление рёбер в граф
        for i, j in self.graph.edges:
            edge = self.graph.edges[i, j]["data"]
            self.visible_edge(net, i, j, edge)

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
        if node.type == "Represent":
            title = (f"ID::{index}\n"
                     f"Layer: #{str(node.layer)[:50]}")
        elif node.type[0] == "NodeInt" or node.type[0] == "NodeVal":
            title = (f"ID::{index}\n"
                     f"Layer: #{str(node.layer)[:50]}\n"
                     f"> {node.text}\n"
                     f"> {node.type[1]}")
        else:
            title = ""

        net.add_node(index, label=node.text, title=title, shape=shape, color=color, size=size)

    @staticmethod
    def visible_edge(net, i, j, edge):
        """
        Добавляет ребро в визуализацию графа.

        Parameters:
        - net (pyvis.network.Network): Объект сети для визуализации графа.
        - index (tuple): Кортеж, представляющий индексы узлов, соединенных
        ребром.
        - edge (dict): Словарь, представляющий ребро графа.
        """
        if edge.type == "Represent":
            title = (f"ID::SRC::{i}\n"
                     f"ID::DST::{j}")
        elif edge.type == "EdgeInt" or edge.type == "EdgeVal":
            title = (f"ID::SRC::{i}\n"
                     f"ID::DST::{j}")
        else:
            title = ""

        net.add_edge(i, j, label=edge.text, title=title)

    def save(self, filename):
        """
        Сохраняет объект Graph в файл.

        Parameters:
        - filename (str): Имя файла для сохранения.
        """
        with open(filename, 'wb') as file:
            pickle.dump({
                "graph": self.graph, "documents": self.documents, "reference": self.reference,
                "static_index": self.static_index, "static_layer": self.static_layer,
            }, file)

    def load(self, filename):
        """
        Загружает объект Graph из файла.

        Parameters:
        - filename (str): Имя файла для загрузки.

        Returns:
        - Graph: Загруженный объект Graph.
        """
        with open(filename, 'rb') as file:
            data = pickle.load(file)
            self.graph        = data["graph"]
            self.documents    = data["documents"]
            self.reference    = data["reference"]
            self.static_index = data["static_index"]
            self.static_layer = data["static_layer"]

    def process_data(self, document):
        """
        Функция для обработки данных из указанного документа.

        Parameters:
        - document (str): Имя документа.

        Returns:
        - tuple: Кортеж, содержащий имя документа и DataFrame с данными о кластерах.
        """
        list_clusters = []

        # Обработка содержимого документа с помощью обработки естественного языка
        content = get_document_content(self.documents_folder, document)
        doc = self.nlp(content)

        # Обход предложений в документе и создание кластеров
        for i, sent in enumerate(doc.sents):
            clusters, list_conn = create_clusters(doc, i, sent)
            clusters = self.__process_data_auto_allocation__(clusters, list_conn)
            list_clusters += clusters

        return doc, list_clusters

    @staticmethod
    def __process_data_auto_allocation__(clusters, list_conn):
        """
        Автоматическое выделение интентов и значений для каждого кластера.

        Parameters:
        - clusters (list): Список кластеров.

        Returns:
        - list: Список автоматически выделенных кластеров.
        """
        parent = []
        child = []
        for conn in list_conn:
            parent.append(conn[0])
            child.append(conn[1])

        for cluster in clusters:
            if cluster.f_type == ClusterType.Null:
                cluster.f_intent = [False, False]
                cluster.f_value  = [False, False]
            if cluster.f_type == ClusterType.TokenClusterQuoted or cluster.f_type == ClusterType.NamedEntity:
                if has_common_element(cluster.index, parent):
                    cluster.f_intent = [True, False]
                else:
                    cluster.f_intent = [False, True]
                if has_common_element(cluster.index, child):
                    cluster.f_value = [True, False]
                else:
                    cluster.f_value = [True, True]
            if cluster.f_type == ClusterType.TokenCluster or cluster.f_type == ClusterType.Word:
                if has_common_element(cluster.index, parent) or has_common_element(cluster.index, child):
                    if has_common_element(cluster.index, parent):
                        cluster.f_intent = [True, False]
                        cluster.f_value = [False, True]
                    else:
                        cluster.f_intent = [False, True]
                        cluster.f_value = [True, False]
                else:
                    cluster.f_intent = [True, True]
                    cluster.f_value = [True, True]
            if cluster.f_type == ClusterType.Number:
                cluster.f_intent = [False, False]
                cluster.f_value = [True, True]

            if not cluster.connect_index:
                cluster.f_value = [False, False]

        return clusters

    def load_data(self, document, clusters):
        self.__load_data_document__(document)
        self.__load_data_reference__(clusters)

        for cluster in clusters:
            self.documents[document].add(self.static_layer + cluster.layer)

        node_list = [[], []]
        self.__load_data_clusters_node_intent__(clusters, node_list)
        self.__load_data_clusters_node_meaning__(clusters, node_list)
        self.__load_data_clusters_edge__(clusters, node_list)

        layer = max([cluster.layer for cluster in clusters])
        self.static_layer += layer + 1

    def __load_data_document__(self, document):
        if document in self.documents:
            self.delete_data(document)
        self.documents[document] = set()

    def __load_data_reference__(self, clusters):
        for cluster in clusters:
            name  = cluster.p_name
            lemma = cluster.p_lemma

            if cluster.f_intent[0]:
                if name not in self.reference:
                    self.reference[name] = set()
                if lemma not in self.reference[name]:
                    self.reference[name].add(lemma)
            else:
                pass

    def __load_data_clusters_node_intent__(self, clusters, node_list):
        clusters_tmp = [cluster for cluster in clusters if cluster.f_intent[0]]

        for cluster in clusters_tmp:
            name  = "REPRESENT::" + cluster.p_name
            lemma = "NODE::INT::" + cluster.p_lemma
            if cluster.f_value[0]:
                lemma += "-Meaning"
            else:
                lemma += "-Intent"

            self.__load_data_node__(
                None, None, name, "Represent", cluster.p_name, self.static_layer + cluster.layer, None, None
            )
            self.__load_data_node__(
                node_list, cluster, lemma, "NodeInt", cluster.p_lemma, self.static_layer + cluster.layer, cluster.f_intent[0], cluster.f_value[0]
            )

            if not self.graph.has_edge(name, lemma):
                self.graph.add_edge(name, lemma, data=GraphEdge("Represent", None))
            if not self.graph.has_edge(lemma, name):
                self.graph.add_edge(lemma, name, data=GraphEdge("Represent", None))

    def __load_data_clusters_node_meaning__(self, clusters, node_list):
        clusters_tmp_l     = [cluster for cluster in clusters if not cluster.f_intent[0]]

        cluster_processing = True
        while cluster_processing:
            clusters_tmp_n     = []
            cluster_processing = False

            for cluster in clusters_tmp_l:
                for node in node_list[1]:
                    if node[1] in cluster.index:
                        parent             = node[0]
                        cluster_processing = True

                        nodes = [edge[1] for edge in list(self.graph.out_edges(parent))]
                        for i in nodes:
                            if self.graph.nodes[i]["data"].text == cluster.p_lemma:
                                self.__load_data_node__(
                                    node_list, cluster, i, "NodeVal", cluster.p_lemma, self.static_layer + cluster.layer, cluster.f_intent[0], cluster.f_value[0]
                                )
                                break
                        else:
                            self.__load_data_node__(
                                node_list, cluster, self.static_index, "NodeVal", cluster.p_lemma, self.static_layer + cluster.layer, cluster.f_intent[0], cluster.f_value[0]
                            )
                            self.graph.add_edge(parent, self.static_index, data=GraphEdge("EdgeVal", None))
                            self.static_index += 1

                        break
                else:
                    clusters_tmp_n.append(cluster)
                    continue

            clusters_tmp_l = clusters_tmp_n

        cluster_processing = True
        while cluster_processing:
            clusters_tmp_n     = []
            cluster_processing = False

            for cluster in clusters_tmp_l:
                connect = cluster.connect_index
                for node in node_list[0]:
                    if has_common_element(connect, node[1]):
                        child              = node[0]
                        cluster_processing = True

                        nodes = [edge[0] for edge in list(self.graph.in_edges(child))]
                        for i in nodes:
                            if self.graph.nodes[i]["data"].text == cluster.p_lemma:
                                self.__load_data_node__(
                                    node_list, cluster, i, "NodeVal", cluster.p_lemma, self.static_layer + cluster.layer,
                                    cluster.f_intent[0], cluster.f_value[0]
                                )
                                break
                        else:
                            self.__load_data_node__(
                                node_list, cluster, self.static_index, "NodeVal", cluster.p_lemma, self.static_layer + cluster.layer,
                                cluster.f_intent[0], cluster.f_value[0]
                            )
                            self.graph.add_edge(self.static_index, child, data=GraphEdge("EdgeVal", None))
                            self.static_index += 1
                        break
                else:
                    if connect:
                        clusters_tmp_n.append(cluster)
                    continue

            clusters_tmp_l = clusters_tmp_n

    def __load_data_clusters_edge__(self, clusters, node_list):
        for cluster in clusters:
            connect = cluster.connect_index

            for node in node_list[0]:
                if has_common_element(connect, node[1]):
                    current = [node[0] for node in node_list[0] if cluster.index == node[1]][0]
                    connect = node[0]

                    if not self.graph.has_edge(current, connect):
                        self.graph.add_edge(current, connect, data=GraphEdge("EdgeInt", None))
                    break

    def __load_data_node__(self, node_list, cluster, id_, type_, text_, layer_, intent_, value_):
        if cluster:
            node_list[0].append((id_, cluster.index))
        if cluster and cluster.connect_index:
            node_list[1].append((id_, cluster.connect_index[0]))

        if not self.graph.has_node(id_):
            self.graph.add_node(id_, data=GraphNode(type_, text_, layer_, intent_, value_))
        elif layer_ not in self.graph.nodes[id_]["data"].layer:
            self.graph.nodes[id_]["data"].layer.append(layer_)

    def delete_data(self, document):
        """
        Функция для удаления данных, связанных с указанным документом.

        Parameters:
        - document (str): Имя документа.
        """
        if document not in self.documents:
            return
        nodes_to_remove = []
        layer_step      = len(self.documents[document])
        layer_border    = min(self.documents[document])

        for i in self.graph.nodes:
            layer = [
                layer - layer_step if layer > layer_border else layer
                for layer in self.graph.nodes[i]["data"].layer if layer not in self.documents[document]
            ]
            if layer:
                self.graph.nodes[i]["data"].layer = layer
            else:
                nodes_to_remove.append(i)
        for node in nodes_to_remove:
            self.graph.remove_node(node)

        documents    = {}
        for key, values in self.documents.items():
            if key != document:
                documents[key] = set([
                    index - layer_step if index > layer_border else index for index in values
                ])
        self.documents = documents

        reference       = {}
        for key, values in self.reference.items():
            if self.graph.has_node("REPRESENT::" + key):
                reference[key] = set()
            for value in values:
                if self.graph.has_node("NODE::INT::" + value + "-Meaning"):
                    reference[key].add(value)
                    continue
                if self.graph.has_node("NODE::INT::" + value + "-Intent"):
                    reference[key].add(value)
                    continue
        self.reference = reference

        self.static_layer -= layer_step

    def search(self, request, flag=False):
        """
        Функция для поиска информации в графе на основе запроса.

        Parameters:
        - request (list): Список запросов.

        Returns:
        - list: Обновленный список запросов с найденной информацией.
        """

        # Список для хранения слоев, связанных с запросом
        if flag:
            request_layer = list(range(self.static_layer))
        else:
            request_layer = []
            # Обработка каждого запроса
            for req in request:
                if req["meaning"] is None:
                    continue
                if "type" in req and req["type"] == "REPRESENT":
                    name = f"""REPRESENT::{req["intent"]}"""
                    request_layer.append(sorted(list(set(self.__search_represent_filter__(name, req)))))
                else:
                    lemma_intent  = f"""NODE::INT::{req["intent"]}-Intent"""
                    lemma_meaning = f"""NODE::INT::{req["intent"]}-Meaning"""
                    if self.graph.has_node(lemma_intent) or self.graph.has_node(lemma_meaning):
                        request_layer.append(sorted(list(set(
                            self.__search_node_filter__(lemma_intent, req) +
                            self.__search_node_filter__(lemma_meaning, req)
                        ))))
                    else:
                        request_layer.append([])
                        break
            print(request_layer)
            print()

            # Находим общие слои для всех запросов
            if request_layer:
                request_layer = list(set(request_layer[0]).intersection(*request_layer[1:]))
            if not request_layer:
                return request
        # Обновляем запросы с найденной информацией
        for req in request:
            if req["meaning"] is not None:
                continue
            if "type" in req and req["type"] == "REPRESENT":
                name = f"""REPRESENT::{req["intent"]}"""
                self.__search_represent_update__(name, req, request_layer)
            else:
                lemma_intent  = f"""NODE::INT::{req["intent"]}-Intent"""
                lemma_meaning = f"""NODE::INT::{req["intent"]}-Meaning"""
                self.__search_node_update__(lemma_intent, req, request_layer)
                self.__search_node_update__(lemma_meaning, req, request_layer)
            req["meaning"] = list(set(req["meaning"])) if req["meaning"] else None
        return request

    def __search_represent_filter__(self, i, request):
        layer = []
        if self.graph.has_node(i):  # and request["meaning"] is not None:
            represent_edge = list(self.graph.in_edges(i))
            for edge in represent_edge:
                in_edges  = list(self.graph.in_edges(edge[0]))
                out_edges = list(self.graph.out_edges(edge[0]))
                for in_edge in in_edges:
                    in_node = self.graph.nodes[in_edge[0]]["data"]
                    if in_node.is_meaning and in_node.text in request["meaning"]:
                        layer += in_node.layer
        return sorted(list(set(layer)))

    def __search_node_filter__(self, i, request):
        layer = []
        if self.graph.has_node(i):  # and request["meaning"] is not None:
            in_edges  = list(self.graph.in_edges(i))
            out_edges = list(self.graph.out_edges(i))
            for in_edge in in_edges:
                in_node = self.graph.nodes[in_edge[0]]["data"]
                if in_node.is_meaning and in_node.text in request["meaning"]:
                    layer += in_node.layer
        return sorted(list(set(layer)))

    def __search_represent_update__(self, i, request, layer):
        if self.graph.has_node(i):  # and request["meaning"] is None:
            represent_edge = list(self.graph.in_edges(i))
            for edge in represent_edge:
                in_edges  = list(self.graph.in_edges(edge[0]))
                out_edges = list(self.graph.out_edges(edge[0]))
                for in_edge in in_edges:
                    in_node = self.graph.nodes[in_edge[0]]["data"]
                    if in_node.is_meaning and has_common_element(in_node.layer, layer):
                        if request["meaning"] is None:
                            request["meaning"] = [in_node.text]
                        else:
                            request["meaning"].append(in_node.text)

    def __search_node_update__(self, i, request, layer):
        if self.graph.has_node(i):  # and request["meaning"] is None:
            in_edges  = list(self.graph.in_edges(i))
            out_edges = list(self.graph.out_edges(i))
            for in_edge in in_edges:
                in_node = self.graph.nodes[in_edge[0]]["data"]
                if in_node.is_meaning and has_common_element(in_node.layer, layer):
                    if request["meaning"] is None:
                        request["meaning"] = [in_node.text]
                    else:
                        request["meaning"].append(in_node.text)

    def processing_text(self, text, is_stop=True, is_punct=False, is_space=False):
        doc = self.nlp(text)
        content = ""

        for sent in doc.sents:
            for word in sent:
                if not is_stop and word.is_stop:
                    continue
                if not is_punct and word.is_punct:
                    continue
                if not is_space and word.is_space:
                    continue
                content += word.lemma_ + " "
            content = content[:-1] + ". "

        print("content")
        print(content)
        return content[:-2]

    def is_reference_name(self, name):
        return name in self.reference

    def is_reference_lemma(self, lemma):
        for values in self.reference.values():
            if lemma in values:
                return True
        return False

    def get_reference_lemma(self, lemma):
        for key, values in self.reference.items():
            if lemma in values:
                return key
        return None

    def get_documents(self, sort=True):
        data = [doc for doc in self.documents]
        return sorted(data) if sort else data

    @property
    def nodes(self):
        return self.graph.nodes

    @property
    def nodes_data(self):
        texts = {}
        nodes = []
        for i in self.graph.nodes:
            node = self.graph.nodes[i]["data"]
            if node.is_intent:
                if node.text in texts:
                    node = GraphNode(
                        "", node.text,
                        sorted(list(set(nodes[texts[node.text]].layer + node.layer))),
                        True, True
                    )
                    nodes[texts[node.text]] = node
                else:
                    texts[node.text] = len(nodes)
                    nodes.append(node)
            else:
                nodes.append(node)
        # return [
        #     self.graph.nodes[i]["data"] for i in self.graph.nodes
        # ]
        return nodes

    @property
    def nodes_intent(self):
        texts = {}
        nodes = []
        for i in self.graph.nodes:
            if self.graph.nodes[i]["data"].is_intent:
                node = self.graph.nodes[i]["data"]
            else:
                continue

            if node.text in texts:
                node = GraphNode(
                    None, node.text,
                    sorted(list(set(nodes[texts[node.text]].layer + node.layer))),
                    True, True
                )
                nodes[texts[node.text]] = node
            else:
                texts[node.text] = len(nodes)
                nodes.append(node)
        # return [
        #     self.graph.nodes[i]["data"] for i in self.graph.nodes if self.graph.nodes[i]["data"].is_intent
        # ]
        return nodes

    @property
    def nodes_intent_text(self):
        texts = []
        for i in self.graph.nodes:
            if self.graph.nodes[i]["data"].is_intent and self.graph.nodes[i]["data"].text not in texts:
                texts.append(self.graph.nodes[i]["data"].text)
            else:
                continue
        # return [
        #     self.graph.nodes[i]["data"].text for i in self.graph.nodes if self.graph.nodes[i]["data"].is_intent
        # ]
        return texts

    @property
    def nodes_meaning(self):
        return [
            self.graph.nodes[i]["data"] for i in self.graph.nodes if self.graph.nodes[i]["data"].is_meaning
        ]

    @property
    def nodes_meaning_text(self):
        return [
            self.graph.nodes[i]["data"].text for i in self.graph.nodes if self.graph.nodes[i]["data"].is_meaning
        ]

    def node_parsing(self, i):
        if self.graph.has_node(i):
            node = self.graph.nodes[i]["data"]
            return {
                "id":      i,
                "type":    node.type,
                "text":    node.text,
                "layer":   node.layer,
                "intent":  node.is_intent,
                "meaning": node.is_meaning
            }
        return None

    @property
    def edges(self):
        return self.graph.edges

    @property
    def edges_data(self):
        texts = {}
        edges = []
        for i, j in self.graph.edges:
            node_l = self.graph.nodes[i]["data"]
            node_r = self.graph.nodes[j]["data"]
            index_l = node_l.text if node_l.is_intent else f"ID::{i}"
            index_r = node_r.text if node_r.is_intent else f"ID::{j}"
            index   = (index_l, index_r)
            if node_l.is_intent or node_r.is_intent:
                if index in texts:
                    edge = edges[texts[index]]
                    if node_l.is_intent and edge[0].is_meaning != node_l.is_meaning:
                        node_l = GraphNode(
                            "", node_l.text,
                            sorted(list(set(edge[0].layer + node_l.layer))),
                            True, True
                        )
                    if node_r.is_intent and edge[1].is_meaning != node_r.is_meaning:
                        node_r = GraphNode(
                            "", node_r.text,
                            sorted(list(set(edge[1].layer + node_r.layer))),
                            True, True
                        )
                    edges[texts[index]] = (node_l, node_r)
                else:
                    texts[index] = len(edges)
                    edges.append((node_l, node_r))
            else:
                edges.append((node_l, node_r))
        # nodes = self.graph.nodes
        # return [
        #     (nodes[i]["data"], nodes[j]["data"]) for i, j in self.graph.edges
        # ]
        return edges

    def edge_parsing(self, i, j):
        if self.graph.has_edge(i, j):
            edge = self.graph.edges[i, j]["data"]
            return {
                "id src":  i,
                "id dest": j,
                "type":    edge.type,
                "text":    edge.text,
            }
        return None
