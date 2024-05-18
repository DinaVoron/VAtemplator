from spacy.symbols import NOUN, PRON, PROPN
from enum import Enum


class ClusterType(Enum):
    Null = 0
    TokenClusterQuoted = 1
    NamedEntity = 2
    TokenCluster = 3
    Word = 4
    Number = 5
    Custom = 6


class Token:
    def __init__(self, elem):
        self.index     = elem.i
        self.lemma     = elem.lemma_
        self.con_index = elem.head.i
        self.con_dep   = elem.dep_

    def __repr__(self):
        return f"{self.lemma}"


class Cluster:
    def __init__(self, layer, cluster_type=ClusterType.Null):
        self.tokens  = []
        self.p_name  = ""
        self.p_lemma = ""
        self.layer   = layer

        self.f_type   = cluster_type
        self.f_intent = [False, True]  # Флаг, Можно ли вносить изменения
        self.f_value  = [False, True]  # Флаг, Можно ли вносить изменения

    def __repr__(self):
        return f"{self.p_name} {self.p_lemma} :: {self.f_type} {self.f_intent} {self.f_value} :: {self.tokens}"

    def empty(self):
        if self.tokens:
            return False
        return True

    def append(self, token):
        self.tokens.append(token)

    def insert(self, token):
        self.tokens.append(token)
        self.tokens.sort(key=lambda x: x.index)

        self.f_type      = ClusterType.Custom
        self.f_intent[1] = True
        self.f_value[1]  = True

    def remove(self, token):
        if token in self.tokens:
            self.tokens.remove(token)

    @property
    def index(self):
        index = [token.index for token in self.tokens]
        return index

    @property
    def lemma(self):
        lemma = [token.lemma for token in self.tokens]
        return lemma

    @property
    def connect_index(self):
        index = [token.con_index for token in self.tokens if token.con_index not in self.index]
        return list(set(index))

    @property
    def connect_dep(self):
        dep = [token.con_dep for token in self.tokens if token.con_index not in self.index]
        return list(set(dep))


def resolve_connect(doc, sent):
    """
    Функция для разрешения равнозначных связей в предложении, сохраняя
    структуру дерева зависимостей.

    Parameters:
    - doc (spacy.Doc): Объект документа SpaCy, содержащий анализируемый текст.
    - sent (spacy.Span): Предложение SpaCy.

    Returns:
    - list_node[0] (list): Список кортежей, представляющих связи между токенами с учетом разрешенных равнозначных связей.
    """
    conj = doc.vocab.strings.add("conj")
    root = doc.vocab.strings.add("ROOT")

    # list_conn[0] содержит исходные связи
    # list_conn[1] используется для временного хранения токенов с равнозначными связями
    list_conn = [set(), set()]

    for i, word in enumerate(sent):
        dep = word.dep
        head = word.head

        # Пропускаем токены с равнозначными связями и некоторые типы токенов
        while dep == conj or head.is_stop or head.is_punct or head.is_digit:
            if dep == root:
                break
            if dep == conj:
                list_conn[1].add(head.i)
                list_conn[1].add(word.i)
            dep = head.dep
            head = head.head

        if word.is_digit:
            list_conn[1].add(word.i)
        for node in list_conn[1]:
            list_conn[0].add((head.i, node))
        list_conn[1].clear()

        word.head = head  # Устанавливаем нового родительского токена
        word.dep = dep    # Устанавливаем новую связь

    return sorted(list_conn[0])  # Возвращаем отсортированный список связей


def create_quoted_clusters(doc, sent):
    list_clusters = []
    cluster = None

    for word in sent:
        if word.text == '"':
            if cluster is None:
                cluster = Cluster(0, cluster_type=ClusterType.Null)
            else:
                list_clusters.append(cluster)
                cluster = None
        else:
            if cluster is not None:
                cluster.append(Token(word))

    if cluster is not None:
        list_clusters.append(cluster)

    return remove_subsets_clusters(list_clusters)


def create_clusters_entity(doc, sent):
    """
    Функция для создания списка кластеров именованных сущностей на основе предложения.

    Parameters:
    - doc (spacy.Doc): Объект документа SpaCy, содержащий анализируемый текст.
    - sent (spacy.Span): Предложение SpaCy, для которого создаются кластеры
    сущностей.

    Returns:
    - list_token (list): Список кластеров именованных сущностей в предложении.
    """
    list_clusters = []  # Список кластеров сущностей
    cluster = None      # Текущий кластер сущностей
    index = 0           # Индекс текущей сущности

    # Проходим по каждому слову в предложении
    for i, word in enumerate(sent):
        # Пропускаем стоп-слова, пунктуацию и цифры
        if word.is_stop or word.is_punct or word.is_digit:
            if cluster is not None:
                list_clusters.append(cluster)
                cluster = None
            continue
        # Проверяем каждую сущность в предложении
        for j, entity in enumerate(sent.ents):
            # Если слово принадлежит к сущности, добавляем его к кластеру
            if word in entity:
                if cluster is None:
                    cluster = Cluster(0, cluster_type=ClusterType.Null)
                    cluster.append(Token(word))
                    index = j
                else:
                    if index == j:
                        cluster.append(Token(word))
                    else:
                        list_clusters.append(cluster)
                        cluster = Cluster(0, cluster_type=ClusterType.Null)
                        cluster.append(Token(word))
                        index = j
                break

    # Добавляем последний кластер, если он не был добавлен
    if cluster is not None:
        list_clusters.append(cluster)

    return remove_subsets_clusters(list_clusters)


def create_clusters_token(doc, sent):
    """
    Функция для создания списка кластеров токенов на основе предложения.

    Parameters:
    - doc (spacy.Doc): Объект Doc, представляющий обработанный текст.
    - sent (spacy.tokens.span.Span): Предложение в виде объекта Span из
    библиотеки spaCy.

    Returns:
    - list_token (list): Список кластеров токенов.
    """
    # Определение типов зависимостей для разных уровней
    labels_layer_1 = ["nsubj", "dobj", "nsubjpass", "pcomp", "pobj", "dative", "appos", "attr", "ROOT"]
    labels_layer_2 = ["amod", "nmod", "obl", "obj"]
    np_deps_layer_1 = [doc.vocab.strings.add(label) for label in labels_layer_1]
    np_deps_layer_2 = [doc.vocab.strings.add(label) for label in labels_layer_2]

    list_clusters = []  # Список кластеров токенов
    seen = set()        # Множество для отслеживания уже обработанных токенов

    # Проходим по каждому слову в предложении
    for i, word in enumerate(sent):
        # Пропускаем слова, которые не являются существительными или местоимениями, или уже были обработаны
        if word.pos not in (NOUN, PROPN, PRON) or word.i in seen:
            continue
            
        # Создаем новый кластер токенов
        cluster = Cluster(0, cluster_type=ClusterType.Null)
        cluster.append(Token(word))

        # Если зависимость слова входит в первый или второй уровень зависимостей,
        # добавляем слово и его потомков в кластер токенов
        if word.dep in np_deps_layer_1 or word.dep in np_deps_layer_2:
            if any(wrd.i in seen for wrd in word.subtree):
                continue
            if word.dep in np_deps_layer_1:
                seen.update(j for j in range(word.left_edge.i, word.i + 1))
                for j in range(word.left_edge.i, word.i + 1):
                    cluster.append(Token(doc[j]))
            if word.dep in np_deps_layer_2:
                if word.i == word.left_edge.i:
                    if len(list(word.head.children)) == 1:
                        seen.update(j for j in range(word.head.i, word.i + 1))
                        for j in range(word.head.i, word.i + 1):
                            cluster.append(Token(doc[j]))
                    else:
                        seen.update(j for j in range(word.i, word.i + 1))
                        for j in range(word.i, word.i + 1):
                            cluster.append(Token(doc[j]))
                else:
                    seen.update(j for j in range(word.left_edge.i, word.i + 1))
                    for j in range(word.left_edge.i, word.i + 1):
                        cluster.append(Token(doc[j]))
        # Если это не кластер, который мы ожидали, мы его пропускаем
        else:
            # Этап: разрешение равнозначных связей - выполнено
            pass

        list_clusters.append(cluster)

    return remove_subsets_clusters(list_clusters)


def remove_subsets_clusters(clusters):
    """
    Функция для удаления подмножества кластеров из списка кластеров.

    Parameters:
    - clusters (list): Список кластеров, где каждый кластер представляет собой
    объект, имеющий атрибут 'index', содержащий индексы токенов кластера.

    Returns:
    - clusters_res (list): Список кластеров без подмножеств других кластеров.
    """
    list_clusters = []

    for i, cluster_iter in enumerate(clusters):
        is_subset = False
        for j, cluster_ in enumerate(clusters):
            if i != j and set(cluster_iter.index).issubset(set(cluster_.index)):
                is_subset = True
                break
        if not is_subset:
            list_clusters.append(cluster_iter)
    return list_clusters


def create_clusters(doc, layer, sent):
    """
    Функция для создания кластеров токенов на основе предложения, используя
    предварительно определенные кластеры сущностей и кластеры токенов.

    Parameters:
    - doc (spacy.Doc): Объект документа SpaCy, содержащий анализируемый текст.
    - sent (spacy.Span): Предложение SpaCy.

    Returns:
    - clusters (list): Список кластеров токенов.
    - list_node (list): Список кортежей, представляющих связи между токенами с
    учетом разрешенных равнозначных связей.
    """
    is_text_clustering = True

    # Разрешение равнозначных связей в предложении
    list_conn = resolve_connect(doc, sent)

    # Определение кластеров сущностей и кластеров токенов
    if is_text_clustering:
        clusters_quoted = create_quoted_clusters(doc, sent)
        clusters_entity = create_clusters_entity(doc, sent)
        clusters_token  = create_clusters_token(doc, sent)
    else:
        clusters_quoted = []
        clusters_entity = []
        clusters_token  = []

    clusters = []      # Список кластеров токенов
    cluster_index = 0  # Индекс текущего кластера

    for word in sent:
        # Пропуск стоп-слов и пунктуации, разрешение связей в предложении
        if word.is_stop or word.is_punct or word.is_space:
            continue

        # Обработка кластеров ограниченных спец символами
        if is_text_clustering and True:
            # Поиск кластера, к которому принадлежит слово
            cluster_quoted = next((cluster for cluster in clusters_quoted if word.i in cluster.index), None)

            if cluster_quoted:
                index = clusters_quoted.index(cluster_quoted)  # Определение индекса кластера

                if not clusters or clusters[-1].f_type != ClusterType.TokenClusterQuoted or cluster_index != index:
                    # Создание нового кластера
                    clusters.append(Cluster(layer, cluster_type=ClusterType.TokenClusterQuoted))
                    cluster_index = index

                clusters[-1].append(Token(word))
                continue

        # Обработка кластеров именованных сущностей
        if is_text_clustering and not word.is_digit and True:
            # Поиск кластера, к которому принадлежит слово
            cluster_entity = next((cluster for cluster in clusters_entity if word.i in cluster.index), None)

            if cluster_entity:
                index = clusters_entity.index(cluster_entity)  # Определение индекса кластера

                if not clusters or clusters[-1].f_type != ClusterType.NamedEntity or cluster_index != index:
                    # Создание нового кластера
                    clusters.append(Cluster(layer, cluster_type=ClusterType.NamedEntity))
                    cluster_index = index

                clusters[-1].append(Token(word))
                continue

        # Обработка кластеров
        if is_text_clustering and not word.is_digit and True:
            # Поиск кластера, к которому принадлежит слово
            cluster_token = next((cluster for cluster in clusters_token if word.i in cluster.index), None)

            if cluster_token:
                index = clusters_token.index(cluster_token)  # Определение индекса кластера

                if not clusters or clusters[-1].f_type != ClusterType.TokenCluster or cluster_index != index:
                    # Создание нового кластера
                    clusters.append(Cluster(layer, cluster_type=ClusterType.TokenCluster))
                    cluster_index = index

                clusters[-1].append(Token(word))
                continue
        
        # Обработка частей речи
        if word.pos in (NOUN, PROPN, PRON):
            clusters.append(Cluster(layer, cluster_type=ClusterType.Word))
            clusters[-1].append(Token(word))
            continue
        
        # Обработка чисел
        if word.is_digit or word.like_num:
            clusters.append(Cluster(layer, cluster_type=ClusterType.Number))
            clusters[-1].append(Token(word))
            continue

        # Обработка слов связок
        clusters.append(Cluster(layer, cluster_type=ClusterType.Null))
        clusters[-1].append(Token(word))

    return clusters, list_conn
