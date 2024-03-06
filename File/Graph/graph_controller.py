import spacy
import os
from enum import Enum
from src_graph.graph import Graph
from src_graph.graph_element import TokenNode
from src_graph.graph_nlp import ClusterType, create_list_clusters


class FState(Enum):
    Null = 0
    Added = 1
    Changed = 2
    Deleted = 3


class GraphController:
    def __init__(self, documents_folder="./res", model="ru_core_news_sm"):
        """
        Конструктор класса.

        Args:
        - documents_folder (str): Путь до папки с документами.
        """

        self.graph = Graph()
        self.documents_folder = documents_folder
        self.documents = []

        self.nlp = spacy.load(model)
        self.bool_is_print = False

    def update_document(self, file, text):
        if not file or not text:
            return

        doc = self.nlp(text)

        for i, sent in enumerate(doc.sents):
            if self.bool_is_print:
                print(f"Предложение:    {str(i + 1):<9}{175 * '='}")
                print(f"  Длина текста: {len(sent)}")
                print(f"  Текст:        {sent}")

            clusters, list_node = create_list_clusters(doc, sent)

            clusters = auto_allocation_of_intents_and_values(clusters)

            if self.bool_is_print:
                print(f"{200 * '-'}\n  Кластеры:")

                for cluster in clusters:
                    print(f"  {cluster}")

            self.graph.add_tokens_to_graph(clusters)

        self.documents.append((file, FState.Added))

    def get_documents_folder(self):
        return self.documents_folder

    def get_documents(self):
        return self.documents

    # def update(self):
    #     pass

    # def _is_document(self, name):
    #     for tpl in self.documents:
    #         if tpl[0] == name:
    #             return True
    #     return False

    # def clear(self):
    #     pass

    # def save(self):
    #     pass

    # def load(self):
    #     pass


def get_merge_documents(controller):
    documents_from_graph = controller.get_documents()
    documents_from_folder = get_documents_from_folder(controller.get_documents_folder())
    merge_documents = []

    for file, status in documents_from_graph:
        if file in documents_from_folder:
            documents_from_folder.remove(file)
            if status == FState.Deleted:
                merge_documents.append((file, FState.Changed))
            else:
                merge_documents.append((file, status))
            continue
        else:
            if status != FState.Null:
                merge_documents.append((file, FState.Deleted))
            continue
    for file in documents_from_folder:
        merge_documents.append((file, FState.Null))

    return merge_documents


def get_document_content(documents_folder, file):
    file_path = os.path.join(documents_folder, file)
    if not os.path.isfile(file_path):
        return ""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        content = ' '.join(content.split())
        return content


def get_documents_from_folder(documents_folder):
    if not os.path.isdir(documents_folder):
        return []
    files = os.listdir(documents_folder)
    return files


def auto_allocation_of_intents_and_values(tokens):  # , list_head, list_dep
    for token in tokens:
        if token.f_type == ClusterType.PartOfSpeech:
            token.f_node_type = TokenNode.IntentAndMeaning
        if token.f_type == ClusterType.Number:
            token.f_node_type = TokenNode.Meaning
        if token.f_type == ClusterType.NamedEntity:
            token.f_node_type = TokenNode.Intent
        if token.f_type == ClusterType.TokenCluster:
            token.f_node_type = TokenNode.IntentAndMeaning
    return tokens


graph_controller = GraphController()

print(get_merge_documents(graph_controller))

graph_controller.update_document(
    'Текстовый документ.txt',
    get_document_content(
        graph_controller.get_documents_folder(),
        'Текстовый документ.txt'
    ))

print(get_merge_documents(graph_controller))

print(get_merge_documents(graph_controller))

print(get_merge_documents(graph_controller))

print(get_merge_documents(graph_controller))

graph_controller.graph.visible()



# filter = [{
#         "intent": "подготовка",
#         "meaning": ["прикладной математика", "информатика"]
#     }, {
#         "intent": "балл",
#         "meaning": None
#     }, {
#         "intent": "год",
#         "meaning": ["2020", "2022"]
#     }]
# filter = graph.search(filter)
#
# for fltr in filter:
#     print(fltr)
