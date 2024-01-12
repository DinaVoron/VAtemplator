import re
from enum import Enum
import spacy
from spacy.tokens import Span, Doc
from spacy.symbols import NOUN, PRON, PROPN
import networkx as nx
from pyvis.network import Network


class TokenType(Enum):
    Null = 0

    PartOfSpeech = 1
    Number = 2
    NamedEntity = 3
    TokenCluster = 4


class TokenNode(Enum):
    Null = 0

    Intent = 1
    Meaning = 2
    IntentAndMeaning = 3


class TypeEdge(Enum):
    Syntax = 0
    Named = 1


class Token:
    def __init__(self, elem, token_type=TokenType.Null, node_type=TokenNode.Null):
        if elem.is_stop or elem.is_punct:
            self.p_index = [elem.i]
            self.p_text = [elem.text]
            self.p_lemma = [""]
            self.p_pos = [""]
        else:
            self.p_index = [elem.i]
            self.p_text = [elem.text]
            self.p_lemma = [elem.lemma_]
            self.p_pos = [elem.pos_]

        self.p_con_index = [elem.head.i]
        self.p_con_dep = [elem.dep_]

        self.f_token_type = token_type
        self.f_node_type = node_type

    def __repr__(self):
        return \
            f"{str(self.p_index)[:16]:<17}" \
            f"{str(self.p_text)[:40]:<41}" \
            f"{str(self.p_lemma)[:40]:<41}" \
            f"{str(self.p_pos)[:20]:<21}" \
            f" | " \
            f"{str(self.p_con_index):<8}" \
            f"{str(self.p_con_dep)[:16]:<17}" \
            f" | " \
            f"{str(self.f_token_type):<23}" \
            f"{str(self.f_node_type)}"

    def add(self, elem):
        if elem.i not in self.p_index:
            if elem.is_stop or elem.is_punct:
                self.p_index += [elem.i]
                self.p_text += [elem.text]
                self.p_lemma += [""]
                self.p_pos += [""]
            else:
                self.p_index += [elem.i]
                self.p_text += [elem.text]
                self.p_lemma += [elem.lemma_]
                self.p_pos += [elem.pos_]

            self.p_con_index += [elem.head.i]
            self.p_con_dep += [elem.dep_]

    def sort(self):
        combined_arrays = list(zip(self.p_index, self.p_text, self.p_lemma, self.p_pos))
        sorted_combined_arrays = sorted(combined_arrays, key=lambda x: x[0])
        self.p_index, self.p_text, self.p_lemma, self.p_pos = zip(*sorted_combined_arrays)

        index = [i for i, elem in enumerate(self.p_con_index) if elem not in self.p_index]

        if (len(index) == 0):
            self.p_con_index = []
            self.p_con_dep = []
        elif (len(index) == 1):
            self.p_con_index = [self.p_con_index[i] for i in index][0]
            self.p_con_dep = [self.p_con_dep[i] for i in index][0]
        else:
            pass

    def clear(self):
        index = [i for i, elem in enumerate(self.p_con_index) if elem not in self.p_index]
        if (len(index) == 0):
            self.p_con_index = None
            self.p_con_dep = None
        elif (len(index) == 1):
            self.p_con_index = [self.p_con_index[i] for i in index][0]
            self.p_con_dep = [self.p_con_dep[i] for i in index][0]
        else:
            pass

    @property
    def index(self):
        return self.p_index

    @property
    def text(self):
        # " ".join(self.p_text)
        return self.p_text

    @property
    def lemma(self):
        return self.p_lemma

    @property
    def pos(self):
        return self.p_pos

    @property
    def con_index(self):
        return self.p_con_index

    @property
    def con_dep(self):
        return self.p_con_dep


class GraphNode:
    def __init__(self, token):
        self.p_text = token.lemma
        self.p_pos = token.pos
        self.f_type = token.f_node_type

    def is_text(self, text):
        return text == " ".join(self.p_text)

    @property
    def text(self):
        return self.p_text

    @property
    def pos(self):
        return self.p_pos

    @property
    def type(self):
        return self.f_type

    @property
    def is_intent(self):
        return self.f_type == TokenNode.Intent or self.f_type == TokenNode.IntentAndMeaning

    @property
    def is_meaning(self):
        return self.f_type == TokenNode.Meaning or self.f_type == TokenNode.IntentAndMeaning


class GraphEdge:
    def __init__(self, text, type):
        self.p_text = text
        self.f_type = type

    @property
    def text(self):
        return self.p_text

    @property
    def type(self):
        return self.f_type

    @property
    def is_syntax(self):
        return self.f_type == TypeEdge.Syntax

    @property
    def is_named(self):
        return self.f_type == TypeEdge.Named


class Graph:
    def __init__(self):
        self.p_graph = nx.DiGraph()
        self.static_index = 1
        self.static_layer = 1

    def visible(self):
        shape = ["triangle", "dot", "dot", "box"]
        color = ["#ffdd00", "#0055cc", "#00aacc", "#7a6a59"]
        size = [20, 12, 12, 10]

        # Отображение графа
        net = Network(
            height="760px", width="100%", bgcolor="#FFFFFF", font_color="black",
            notebook=False, directed=True, select_menu=True, filter_menu=True
        )
        net.set_options("""const options = {
                          "interaction": {
                            "navigationButtons": true
                          }
                        }""")

        for i in self.p_graph.nodes:
            node = self.p_graph.nodes[i]
            if node['data'].is_intent and not node['data'].is_meaning:
                net.add_node(
                    i,
                    label=" ".join(node['data'].text),
                    title=f"ID: {i}\n" \
                          f"L: #{node['layer']}\n" \
                          f"> {node['data'].text}\n" \
                          f"> {node['data'].pos}\n" \
                          f"> {node['data'].type}",
                    layer=f"#{node['layer']}",
                    shape=shape[0],
                    color=color[0],
                    size=size[0]
                )
            if node['data'].is_intent and node['data'].is_meaning:
                net.add_node(
                    i,
                    label=" ".join(node['data'].text),
                    title=f"ID: {i}\n" \
                          f"L: #{node['layer']}\n" \
                          f"> {node['data'].text}\n" \
                          f"> {node['data'].pos}\n" \
                          f"> {node['data'].type}",
                    layer=f"#{node['layer']}",
                    shape=shape[1],
                    color=color[1],
                    size=size[1]
                )
            if not node['data'].is_intent and node['data'].is_meaning:
                net.add_node(
                    i,
                    label=" ".join(node['data'].text),
                    title=f"ID: {i}\n" \
                          f"L: #{node['layer']}\n" \
                          f"> {node['data'].text}\n" \
                          f"> {node['data'].pos}\n" \
                          f"> {node['data'].type}",
                    layer=f"#{node['layer']}",
                    shape=shape[2],
                    color=color[2],
                    size=size[2]
                )
            if not node['data'].is_intent and not node['data'].is_meaning:
                net.add_node(
                    i,
                    label=" ".join(node['data'].text),
                    title=f"ID: {i}\n" \
                          f"L: #{node['layer']}\n" \
                          f"> {node['data'].text}\n" \
                          f"> {node['data'].pos}\n" \
                          f"> {node['data'].type}",
                    layer=f"#{node['layer']}",
                    shape=shape[3],
                    color=color[3],
                    size=size[3]
                )

        for it in self.p_graph.edges:
            edge = self.p_graph.edges[it[0], it[1]]
            net.add_edge(
                it[0], it[1],
                label=edge['data'].text,

                title=f"ID: {it[0]}/{it[1]}\n" \
                      f"L: #{edge['layer']}\n" \
                      f"> {edge['data'].text}\n" \
                      f"> {edge['data'].type}",
                layer=f"#{edge['layer']}",
            )

        net.show('graph.html', notebook=False)

    def add_tokens_to_graph(self, tokens):
        for i, token in enumerate(tokens):
            if token.f_node_type == TokenNode.Intent or token.f_node_type == TokenNode.IntentAndMeaning:
                token_text = " ".join(token.lemma)
                if self.p_graph.has_node(token_text):
                    if self.static_layer not in self.p_graph.nodes[token_text]['layer']:
                        self.p_graph.nodes[token_text]['layer'] += [self.static_layer]
                else:
                    self.p_graph.add_node(
                        token_text,
                        data=GraphNode(token),
                        layer=[self.static_layer]
                    )
            else:
                self.p_graph.add_node(
                    self.static_index + i,
                    data=GraphNode(token),
                    layer=[self.static_layer]
                )

        for i, token in enumerate(tokens):
            if token.con_index is not None:
                for j, token_iter in enumerate(tokens):
                    if i != j and token.con_index in token_iter.index:
                        if token.f_node_type == TokenNode.Intent or token.f_node_type == TokenNode.IntentAndMeaning:
                            token_text = " ".join(token.lemma)
                            if token_iter.f_node_type == TokenNode.Intent or token_iter.f_node_type == TokenNode.IntentAndMeaning:
                                token_iter_text = " ".join(token_iter.lemma)
                                self.p_graph.add_edge(
                                    token_text,
                                    token_iter_text,
                                    data=GraphEdge(token.con_dep, TypeEdge.Syntax),
                                    layer=self.static_layer
                                )
                            else:
                                self.p_graph.add_edge(
                                    token_text,
                                    self.static_index + j,
                                    data=GraphEdge(token.con_dep, TypeEdge.Syntax),
                                    layer=self.static_layer
                                )
                        else:
                            if token_iter.f_node_type == TokenNode.Intent or token_iter.f_node_type == TokenNode.IntentAndMeaning:
                                token_iter_text = " ".join(token_iter.lemma)
                                self.p_graph.add_edge(
                                    self.static_index + i,
                                    token_iter_text,
                                    data=GraphEdge(token.con_dep, TypeEdge.Syntax),
                                    layer=self.static_layer
                                )
                            else:
                                self.p_graph.add_edge(
                                    self.static_index + i,
                                    self.static_index + j,
                                    data=GraphEdge(token.con_dep, TypeEdge.Syntax),
                                    layer=self.static_layer
                                )
                        break

        self.static_index += len(tokens)
        self.static_layer += 1

    def search(self, filter):
        list_layer = []

        for elem in filter:
            if self.p_graph.has_node(elem["intent"]):
                node_intent = self.p_graph.nodes[elem["intent"]]
            else:
                node_intent = None
            # Входящие связи
            in_edges = list(self.p_graph.in_edges(elem["intent"]))
            # Исходящие связи
            out_edges = list(self.p_graph.out_edges(elem["intent"]))
            if node_intent is not None and node_intent["data"].is_intent:
                if elem["meaning"] is not None:
                    layer = []
                    for meaning in elem["meaning"]:
                        for edge in in_edges:
                            node_in_edge = self.p_graph.nodes[edge[0]]
                            if node_in_edge["data"].is_meaning and node_in_edge["data"].is_text(meaning):
                                layer += node_in_edge["layer"]
                    list_layer.append(sorted(list(set(layer))))
            else:
                list_layer.append([])

        common_set = set(list_layer[0]).intersection(*list_layer[1:])
        result_list_layer = list(common_set)

        for elem in filter:
            if self.p_graph.has_node(elem["intent"]):
                node_intent = self.p_graph.nodes[elem["intent"]]
            else:
                node_intent = None
            # Входящие связи
            in_edges = list(self.p_graph.in_edges(elem["intent"]))
            # Исходящие связи
            out_edges = list(self.p_graph.out_edges(elem["intent"]))
            if node_intent is not None and node_intent["data"].is_intent:
                if elem["meaning"] is None:
                    for edge in in_edges:
                        node_in_edge = self.p_graph.nodes[edge[0]]
                        if node_in_edge["data"].is_meaning and has_common_element(result_list_layer, node_in_edge["layer"]):
                            if elem["meaning"] is None:
                                elem["meaning"] = [" ".join(node_in_edge["data"].text)]
                            else:
                                elem["meaning"].append(" ".join(node_in_edge["data"].text))

        return filter

    @property
    def nodes(self):
        return self.p_graph.nodes

    @property
    def edges(self):
        return self.p_graph.edges

    @property
    def list_intent(self):
        return [self.p_graph.nodes[i]['data'] for i in self.p_graph.nodes if self.p_graph.nodes[i]['data'].is_intent]

    @property
    def list_meaning(self):
        return [self.p_graph.nodes[i]['data'] for i in self.p_graph.nodes if self.p_graph.nodes[i]['data'].is_meaning]

    @property
    def list_intent_text(self):
        return [" ".join(self.p_graph.nodes[i]['data'].text) for i in self.p_graph.nodes if self.p_graph.nodes[i]['data'].is_intent]

    @property
    def list_meaning_text(self):
        return [" ".join(self.p_graph.nodes[i]['data'].text) for i in self.p_graph.nodes if self.p_graph.nodes[i]['data'].is_meaning]

    def parsing_node(self, i):
        if self.p_graph.has_node(i):
            node = self.p_graph.nodes[i]
            return {"text": " ".join(node['data'].text), "layer": node['layer'], "type": node['data'].type,
                    "intent": node['data'].is_intent, "meaning": node['data'].is_meaning}
        return None

    def parsing_edge(self, i, j):
        if self.p_graph.has_edge(i, j):
            edge = self.p_graph.edges[i, j]
            return {"text": edge['data'].text, "layer": edge['layer'], "type": edge['data'].type,
                    "syntax": edge['data'].is_syntax, "named": edge['data'].is_named}
        return None


def filter_list_clusters(list_clusters):
    result_list_clusters = []

    for i, token_chunk_1 in enumerate(list_clusters):
        is_subset = False

        for j, token_chunk_2 in enumerate(list_clusters):
            if i != j and set(token_chunk_1.index).issubset(set(token_chunk_2.index)):
                is_subset = True
                break

        if not is_subset:
            result_list_clusters.append(token_chunk_1)

    return result_list_clusters


def Create_a_list_of_token_clusters(doc, sentence: spacy.tokens.span.Span):
    labels_layer_1 = [
        "nsubj", "dobj", "nsubjpass", "pcomp", "pobj", "dative", "appos", "attr", "ROOT",
    ]
    labels_layer_2 = [
        "amod", "nmod", "obl", "obj",
    ]
    np_deps_layer_1 = [doc.vocab.strings.add(label) for label in labels_layer_1]
    np_deps_layer_2 = [doc.vocab.strings.add(label) for label in labels_layer_2]
    # conj = doc.vocab.strings.add("conj")
    list_token = []
    seen = set()

    for i, word in enumerate(sentence):
        if word.pos not in (NOUN, PROPN, PRON) or word.i in seen:
            continue
        token_chunk = Token(word, token_type=TokenType.TokenCluster)

        if word.dep in np_deps_layer_1 or word.dep in np_deps_layer_2:
            if any(wrd.i in seen for wrd in word.subtree):
                continue
            # seen.update(j for j in range(word.left_edge.i, word.i + 1))
            # for k in range(word.left_edge.i, word.i + 1):
            #     token_chunk.add(doc[k])

            if word.dep in np_deps_layer_1:
                seen.update(j for j in range(word.left_edge.i, word.i + 1))
                for k in range(word.left_edge.i, word.i + 1):
                    token_chunk.add(doc[k])

            if word.dep in np_deps_layer_2:
                if word.i == word.left_edge.i:
                    if len(list(word.head.children)) == 1:
                        seen.update(j for j in range(word.head.i, word.i + 1))
                        for k in range(word.head.i, word.i + 1):
                            token_chunk.add(doc[k])
                    else:
                        seen.update(j for j in range(word.i, word.i + 1))
                        for k in range(word.i, word.i + 1):
                            token_chunk.add(doc[k])
                else:
                    seen.update(j for j in range(word.left_edge.i, word.i + 1))
                    for k in range(word.left_edge.i, word.i + 1):
                        token_chunk.add(doc[k])

        else:
            # if word.dep == conj:
            #     head = word.head
            #     while head.dep == conj and head.head.i < head.i:
            #         head = head.head
            #     if head.dep in np_deps_layer_1 or head.dep in np_deps_layer_2:
            #         if any(w.i in seen for w in word.subtree):
            #             continue
            #         seen.update(j for j in range(word.left_edge.i, word.i + 1))
            #         for k in range(word.left_edge.i, word.i + 1):
            #             token_chunk.add(doc[k])
            pass

        token_chunk.sort()
        list_token += [token_chunk]

    # удаление дубликатов
    list_token = filter_list_clusters(list_token)
    return list_token


def Create_a_list_of_entity_clusters(doc, sentence: spacy.tokens.span.Span):
    list_token = []
    token_chunk = None
    token_ent_i = 0

    for word in sentence:
        if word.is_stop or word.is_punct or word.is_digit:
            if token_chunk is not None:
                list_token += [token_chunk]
                token_chunk = None
            continue

        for i, token_ent in enumerate(sentence.ents):
            if word in token_ent:
                if token_chunk is None:
                    token_ent_i = i
                    token_chunk = Token(word, token_type=TokenType.NamedEntity)
                else:
                    if token_ent_i == i:
                        token_chunk.add(word)
                    else:
                        token_ent_i = i
                        list_token += [token_chunk]
                        token_chunk = Token(word, token_type=TokenType.NamedEntity)
                break

    if token_chunk is not None:
        list_token += [token_chunk]

    for token in list_token:
        token.sort()

    # удаление дубликатов
    list_token = filter_list_clusters(list_token)
    return list_token


def create_list_token(doc, sentence: spacy.tokens.span.Span):
    conj = doc.vocab.strings.add("conj")
    root = doc.vocab.strings.add("ROOT")
    list_dep = []
    list_head = []

    for i, word in enumerate(sentence):
        if word.is_digit:
            list_dep += [(word.i, "")]

        dep = word.dep
        head = word.head
        fl = False

        while dep == conj or dep != root and (head.is_stop or head.is_punct or head.is_digit):
            if not fl:
                if dep == conj:
                    list_dep += [(word.i, "")]
                    list_dep += [(head.i, "")]
                    fl = True
            else:
                list_dep += [(head.i, "")]

            dep = head.dep
            head = head.head

        if fl or word.is_digit:
            list_head += [head.i]
        word.dep = dep
        word.head = head
    list_dep = sorted(set(list_dep))
    list_head = sorted(set(list_head))

    list_entity_clusters = Create_a_list_of_entity_clusters(doc, sentence)
    list_token_clusters = Create_a_list_of_token_clusters(doc, sentence)

    list_token = []
    token = None
    entity_cluster_index = 0
    token_cluster_index = 0

    for i, word in enumerate(sentence):
        fl = False

        if word.is_stop or word.is_punct:
            continue

        if not fl and not word.is_digit:
            for j, entity_cluster in enumerate(list_entity_clusters):
                if word.i in entity_cluster.index:
                    if token is None:
                        entity_cluster_index = j
                        token = Token(word, token_type=TokenType.NamedEntity)
                    else:
                        if token.f_token_type == TokenType.NamedEntity and entity_cluster_index == j:
                            token.add(word)
                        else:
                            list_token += [token]
                            entity_cluster_index = j
                            token = Token(word, token_type=TokenType.NamedEntity)
                    fl = True
                    break

        if not fl and not word.is_digit:
            for j, token_cluster in enumerate(list_token_clusters):
                if word.i in token_cluster.index:
                    if token is None:
                        token_cluster_index = j
                        token = Token(word, token_type=TokenType.TokenCluster)
                    else:
                        if token.f_token_type == TokenType.TokenCluster and token_cluster_index == j:
                            token.add(word)
                        else:
                            list_token += [token]
                            token_cluster_index = j
                            token = Token(word, token_type=TokenType.TokenCluster)
                    fl = True
                    break

        if not fl and not word.is_digit:
            if word.pos in (NOUN, PROPN, PRON):
                if token is None:
                    list_token += [Token(word, token_type=TokenType.PartOfSpeech)]
                else:
                    list_token += [token, Token(word, token_type=TokenType.PartOfSpeech)]
                    token = None

        if not fl:
            if word.is_digit:
                if token is None:
                    list_token += [Token(word, token_type=TokenType.Number)]
                else:
                    list_token += [token, Token(word, token_type=TokenType.Number)]
                    token = None
            else:
                if token is None:
                    list_token += [Token(word, token_type=TokenType.Null)]
                else:
                    list_token += [token, Token(word, token_type=TokenType.Null)]
                    token = None

    if token is not None:
        list_token += [token]
    for token in list_token:
        token.clear()

    return list_token, list_head, list_dep


def auto_allocation_of_intents_and_values(tokens, list_head, list_dep):
    for token in tokens:
        if token.f_token_type == TokenType.PartOfSpeech:
            token.f_node_type = TokenNode.IntentAndMeaning
        if token.f_token_type == TokenType.Number:
            token.f_node_type = TokenNode.Meaning
        if token.f_token_type == TokenType.NamedEntity:
            token.f_node_type = TokenNode.Intent
        if token.f_token_type == TokenType.TokenCluster:
            token.f_node_type = TokenNode.IntentAndMeaning
    return tokens


def has_common_element(array1, array2):
    for element in array1:
        if element in array2:
            return True
    return False


def init_graph():
    return Graph()


def graph_nlp_text(graph, text):
    bool_is_print = False

    text = re.sub(r"\s+", " ", text, flags=re.DOTALL)

    nlp = spacy.load("ru_core_news_sm")
    doc = nlp(text)

    for index, sent in enumerate(doc.sents):
        if bool_is_print:
            print(f"Предложение:    {str(index + 1):<9}{175 * '='}")
            print(f"  Текст:        {sent}")
            print(f"  Длина текста: {len(sent)}")

        tokens, heads, deps = create_list_token(doc, sent)
        tokens = auto_allocation_of_intents_and_values(tokens, heads, deps)

        if bool_is_print:
            print(f"{200 * '-'}\n  Кластеры токенов:")
            for token in tokens:
                print(f"  {token}")

        graph.add_tokens_to_graph(tokens)

    return graph


'''# text = """Проходные баллы по направлению подготовки бакалавриата и специалитета за 2020, 2021, 2022, 2023 год.
#     Правила приема в ДВФУ на обучение по программам бакалавриата в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
#     Правила приема в ДВФУ на обучение по программам специалитета в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
#     Правила приема в ДВФУ на обучение по программам магистратуры в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
#     Правила приема в ДВФУ на обучение по программам подготовки научных кадров в аспирантуре в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
#     Правила приема в ДВФУ на обучение по программам подготовки научно-педагогических кадров в аспирантуре в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
#     Правила приема в ДВФУ в 2023 году определяют особенности приема на первый курс в 2023/2024 учебном году на места в рамках контрольных цифр приема на обучение за счет бюджетных ассигнований федерального бюджета и по договорам об образовании, заключаемым при приеме на обучение за счет средств физических или юридических лиц.
#     Правила приема в ДВФУ в 2023 году определяют особенности приема на первый курс в 2023/2024 учебном году на обучение за счет бюджетных ассигнований федерального бюджета и по договорам об образовании для следующих категорий граждан: обучавшихся в организациях осуществляющих образовательную деятельность, завершивших освоение образовательных программ среднего общего образования и успешно прошедших государственную итоговую аттестацию, проходивших обучение за рубежом и вынужденных прервать его в связи с недружественными действиями иностранных государств.
#     Обучавшихся в организациях осуществляющих образовательную деятельность, расположенных на территориях Донецкой Народной Республики, Луганской Народной Республики, Запорожской области, Херсонской области.
#     Завершивших освоение образовательных программ среднего общего образования и успешно прошедших государственную итоговую аттестацию на территориях Донецкой Народной Республики, Луганской Народной Республики, Запорожской области, Херсонской области.
#     Проходивших обучение за рубежом и вынужденных прервать его в связи с недружественными действиями иностранных государств, на основании частей 7 и 8 статьи 5 Федерального закона от 17 февраля 2023 г. № 19-ФЗ «Об особенностях правового регулирования отношений в сферах образования и науки», а также постановления Правительства Российской Федерации от 3 апреля 2023 г. № 528 «Об утверждении особенностей приема на обучение по образовательным программам высшего образования в 2023 году».
#     """
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

filter = [{
        "intent": "подготовка",
        "meaning": ["прикладной математика", "информатика"]
    }, {
        "intent": "балл",
        "meaning": None
    }, {
        "intent": "год",
        "meaning": ["2022"]
    }]
filter = graph.search(filter)

for fltr in filter:
    print(fltr)

graph.visible()'''