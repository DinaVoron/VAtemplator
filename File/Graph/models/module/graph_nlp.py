import spacy
from spacy.tokens import Span, Doc
from spacy.symbols import NOUN, PRON, PROPN
from enum import Enum


class ClusterType(Enum):
    Null = 0
    TokenCluster = 1
    TokenClusterQuoted = 2
    NamedEntity = 3
    PartOfSpeech = 4
    Number = 5


class Token:
    # p_index       [int]   Индекс
    # p_text        [str]   Текст
    # p_lemma       [str]   Начальная форма
    # p_pos         [str]   Часть речи
    # p_con_index   [int]   Связь с другим индексом
    # p_con_dep     [str]   Название связи
    # f_type        enum    Тип кластера

    def __init__(self, elem_str, cluster_type=ClusterType.Null):
        self.p_index     = [elem_str.i]
        self.p_text      = [elem_str.text]
        self.p_con_index = [elem_str.head.i]
        self.p_con_dep   = [elem_str.dep_]
        self.f_type      = cluster_type
        self.f_intent    = False
        self.f_value     = False

        if not elem_str.is_stop and not elem_str.is_punct:
            self.p_lemma = [elem_str.lemma_]
            self.p_pos   = [elem_str.pos_]
        else:
            self.p_lemma = [None]
            self.p_pos   = [None]

    def __repr__(self):
        return \
            f"{str(self.p_index)[:16]:<17} {str(self.p_text)[:40]:<41}" \
            f"{str(self.p_lemma)[:40]:<41} {str(self.p_pos)[:20]:<21} | " \
            f"{str(self.p_con_index):<8} {str(self.p_con_dep)[:16]:<17} | " \
            f"{str(self.f_type)}"

    def append(self, elem_str):
        if elem_str.i not in self.p_index:
            self.p_index     += [elem_str.i]
            self.p_text      += [elem_str.text]
            self.p_con_index += [elem_str.head.i]
            self.p_con_dep   += [elem_str.dep_]

            if not elem_str.is_stop and not elem_str.is_punct:
                self.p_lemma += [elem_str.lemma_]
                self.p_pos   += [elem_str.pos_]
            else:
                self.p_lemma += [None]
                self.p_pos   += [None]

    def sort_connect(self):
        combined_arrays = list(zip(self.p_index, self.p_text, self.p_lemma, self.p_pos))
        sorted_combined_arrays = sorted(combined_arrays, key=lambda elem: elem[0])
        self.p_index, self.p_text, self.p_lemma, self.p_pos = zip(*sorted_combined_arrays)

    def remove_connect(self):
        connect = [[index, dep] for index, dep in zip(self.p_con_index, self.p_con_dep) if index not in self.p_index]
        if connect:
            self.p_con_index, self.p_con_dep = connect[0]
        else:
            self.p_con_index, self.p_con_dep = [[], []]

    @property
    def index(self):
        return self.p_index

    @property
    def text(self):
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


def resolve_connect(doc, sent):
    """
    Функция для разрешения равнозначных связей в предложении, сохраняя структуру дерева зависимостей.

    Parameters:
    - doc (spacy.Doc): Объект документа SpaCy, содержащий анализируемый текст.
    - sent (spacy.Span): Предложение SpaCy.

    Returns:
    - list_node[0] (list): Список кортежей, представляющих связи между токенами с учетом разрешенных равнозначных
    связей.
    """

    conj = doc.vocab.strings.add("conj")
    root = doc.vocab.strings.add("ROOT")

    # list_node[0] содержит исходные связи
    # list_node[1] используется для временного хранения токенов с равнозначными связями
    list_node = [set(), set()]

    for i, word in enumerate(sent):
        dep = word.dep
        head = word.head

        # Пропускаем токены с равнозначными связями и некоторые типы токенов
        while dep == conj or head.is_stop or head.is_punct or head.is_digit:
            if dep == root:
                break
            if dep == conj:
                list_node[1].add(head.i)
                list_node[1].add(word.i)
            dep = head.dep
            head = head.head

        if word.is_digit:
            list_node[1].add(word.i)
        for node in list_node[1]:
            list_node[0].add((head.i, node))
        list_node[1].clear()

        word.head = head  # Устанавливаем нового родительского токена
        word.dep = dep  # Устанавливаем новую связь

    return sorted(list_node[0])  # Возвращаем отсортированный список связей


def create_quoted_clusters(doc, sent):
    list_quoted_clusters = []
    quoted_cluster = None

    for i, word in enumerate(sent):
        if word.text == '"':
            if quoted_cluster is None:
                quoted_cluster = Token(word, cluster_type=ClusterType.TokenClusterQuoted)
            else:
                list_quoted_clusters.append(quoted_cluster)
                quoted_cluster = None
        else:
            if quoted_cluster is None:
                pass
            else:
                quoted_cluster.append(word)

    for cluster in list_quoted_clusters:
        cluster.sort_connect()    # Сортировка связей кластера
        cluster.remove_connect()  # Удаление связей

    list_quoted_clusters = remove_subsets_clusters(list_quoted_clusters)
    return list_quoted_clusters


def create_clusters_token(doc, sent):
    """
    Функция для создания списка кластеров токенов на основе предложения.

    Parameters:
    - doc (spacy.Doc): Объект Doc, представляющий обработанный текст.
    - sent (spacy.tokens.span.Span): Предложение в виде объекта Span из библиотеки spaCy.

    Returns:
    - list_token (list): Список кластеров токенов.
    """

    # Определение типов зависимостей для разных уровней
    labels_layer_1 = [
        "nsubj", "dobj", "nsubjpass", "pcomp", "pobj", "dative", "appos", "attr", "ROOT",
    ]
    labels_layer_2 = [
        "amod", "nmod", "obl", "obj",
    ]
    np_deps_layer_1 = [doc.vocab.strings.add(label) for label in labels_layer_1]
    np_deps_layer_2 = [doc.vocab.strings.add(label) for label in labels_layer_2]

    list_token_clusters = []  # Список кластеров токенов
    seen = set()              # Множество для отслеживания уже обработанных токенов

    # Проходим по каждому слову в предложении
    for i, word in enumerate(sent):
        # Пропускаем слова, которые не являются существительными или местоимениями, или уже были обработаны
        if word.pos not in (NOUN, PROPN, PRON) or word.i in seen:
            continue
        # Создаем новый кластер токенов
        token_cluster = Token(word, cluster_type=ClusterType.TokenCluster)

        # Если зависимость слова входит в первый или второй уровень зависимостей,
        # добавляем слово и его потомков в кластер токенов
        if word.dep in np_deps_layer_1 or word.dep in np_deps_layer_2:
            if any(wrd.i in seen for wrd in word.subtree):
                continue
            if word.dep in np_deps_layer_1:
                seen.update(j for j in range(word.left_edge.i, word.i + 1))
                for j in range(word.left_edge.i, word.i + 1):
                    token_cluster.append(doc[j])
            if word.dep in np_deps_layer_2:
                if word.i == word.left_edge.i:
                    if len(list(word.head.children)) == 1:
                        seen.update(j for j in range(word.head.i, word.i + 1))
                        for j in range(word.head.i, word.i + 1):
                            token_cluster.append(doc[j])
                    else:
                        seen.update(j for j in range(word.i, word.i + 1))
                        for j in range(word.i, word.i + 1):
                            token_cluster.append(doc[j])
                else:
                    seen.update(j for j in range(word.left_edge.i, word.i + 1))
                    for j in range(word.left_edge.i, word.i + 1):
                        token_cluster.append(doc[j])
        # Если это не кластер, который мы ожидали, мы его пропускаем
        else:
            # Этап: разрешение равнозначных связей - выполнено
            pass
            # if word.dep == conj:
            #     head = word.head
            #     while head.dep == conj and head.head.i < head.i:
            #         head = head.head
            #     if head.dep in np_deps_layer_1 or head.dep in np_deps_layer_2:
            #         if any(w.i in seen for w in word.subtree):
            #             continue
            #         seen.update(j for j in range(word.left_edge.i, word.i + 1))
            #         for k in range(word.left_edge.i, word.i + 1):
            #             token_cluster.add(doc[k])

        token_cluster.sort_connect()            # Сортировка связей кластера
        token_cluster.remove_connect()          # Удаление связей
        list_token_clusters += [token_cluster]  # Добавление кластера в список кластеров

    list_token_clusters = remove_subsets_clusters(list_token_clusters)  # Удаление подмножеств кластеров
    return list_token_clusters  # Возвращение списка кластеров


def create_clusters_entity(doc, sent):
    """
    Функция для создания списка кластеров именованных сущностей на основе предложения.

    Parameters:
    - doc (spacy.Doc): Объект документа SpaCy, содержащий анализируемый текст.
    - sent (spacy.Span): Предложение SpaCy, для которого создаются кластеры сущностей.

    Returns:
    - list_token (list): Список кластеров именованных сущностей в предложении.
    """

    list_entity_clusters = []  # Список кластеров сущностей
    entity_cluster = None      # Текущий кластер сущностей
    entity_index = 0           # Индекс текущей сущности

    # Проходим по каждому слову в предложении
    for i, word in enumerate(sent):
        # Пропускаем стоп-слова, пунктуацию и цифры
        if word.is_stop or word.is_punct or word.is_digit:
            if entity_cluster is not None:
                list_entity_clusters.append(entity_cluster)
                entity_cluster = None
            continue
        # Проверяем каждую сущность в предложении
        for j, entity in enumerate(sent.ents):
            # Если слово принадлежит к сущности, добавляем его к кластеру
            if word in entity:
                if entity_cluster is None:
                    entity_index = j
                    entity_cluster = Token(word, cluster_type=ClusterType.NamedEntity)
                else:
                    if entity_index == j:
                        entity_cluster.append(word)
                    else:
                        list_entity_clusters.append(entity_cluster)
                        entity_index = j
                        entity_cluster = Token(word, cluster_type=ClusterType.NamedEntity)
                break

    # Добавляем последний кластер, если он не был добавлен
    if entity_cluster is not None:
        list_entity_clusters.append(entity_cluster)

    for cluster in list_entity_clusters:
        cluster.sort_connect()    # Сортировка связей кластера
        cluster.remove_connect()  # Удаление связей

    list_entity_clusters = remove_subsets_clusters(list_entity_clusters)
    return list_entity_clusters


def remove_subsets_clusters(clusters):
    """
    Функция для удаления подмножества кластеров из списка кластеров.

    Parameters:
    - clusters (list): Список кластеров, где каждый кластер представляет собой объект, имеющий атрибут 'index',
    содержащий индексы токенов кластера.

    Returns:
    - clusters_res (list): Список кластеров без подмножеств других кластеров.
    """

    clusters_res = []
    for i, cluster_1 in enumerate(clusters):
        is_subset = False
        for j, cluster_2 in enumerate(clusters):
            if i != j and set(cluster_1.index).issubset(set(cluster_2.index)):
                is_subset = True
                break
        if not is_subset:
            clusters_res.append(cluster_1)
    return clusters_res


def create_clusters(doc, sent):
    """
    Функция для создания кластеров токенов на основе предложения, используя предварительно определенные
    кластеры сущностей и кластеры токенов.

    Parameters:
    - doc (spacy.Doc): Объект документа SpaCy, содержащий анализируемый текст.
    - sent (spacy.Span): Предложение SpaCy.

    Returns:
    - clusters (list): Список кластеров токенов.
    - list_node (list): Список кортежей, представляющих связи между токенами с учетом разрешенных равнозначных связей.
    """

    # Разрешение равнозначных связей в предложении
    list_node = resolve_connect(doc, sent)

    # Определение кластеров сущностей и кластеров токенов
    clusters_entity = create_clusters_entity(doc, sent)
    clusters_token  = create_clusters_token(doc, sent)
    clusters_quoted = create_quoted_clusters(doc, sent)

    clusters      = []  # Список кластеров токенов
    cluster_index = 0   # Индекс текущего кластера

    for word in sent:
        # Пропускаем стоп-слова и пунктуацию
        if word.is_stop or word.is_punct:
            print(word.text)
            continue

        # Обработка кластеров токенов
        if True:
            # Поиск выделенных кластера, к которому принадлежит слово
            cluster_quoted = next((tokens for tokens in clusters_quoted if word.i in tokens.index), None)

            if cluster_quoted:
                # Определение индекса кластера
                cluster_quoted_index = clusters_quoted.index(cluster_quoted)

                # Создание нового кластера или добавление в существующий
                if (
                        not clusters or clusters[-1].f_type != ClusterType.TokenClusterQuoted or
                        cluster_index != cluster_quoted_index
                ):
                    clusters.append(Token(word, cluster_type=ClusterType.TokenClusterQuoted))
                    cluster_index = cluster_quoted_index
                else:
                    clusters[-1].append(word)
                continue

        # Обработка кластеров сущностей
        if not word.is_digit:
            # Поиск кластера сущности, к которому принадлежит слово
            cluster_entity = next((entity for entity in clusters_entity if word.i in entity.index), None)

            if cluster_entity:
                # Определение индекса кластера
                cluster_entity_index = clusters_entity.index(cluster_entity)

                # Создание нового кластера или добавление в существующий
                if (
                        not clusters or clusters[-1].f_type != ClusterType.NamedEntity or
                        cluster_index != cluster_entity_index
                ):
                    clusters.append(Token(word, cluster_type=ClusterType.NamedEntity))
                    cluster_index = cluster_entity_index
                else:
                    clusters[-1].append(word)
                continue

        # Обработка кластеров токенов
        if not word.is_digit:
            # Поиск кластера токена, к которому принадлежит слово
            cluster_token = next((tokens for tokens in clusters_token if word.i in tokens.index), None)

            if cluster_token:
                # Определение индекса кластера
                cluster_token_index = clusters_token.index(cluster_token)

                # Создание нового кластера или добавление в существующий
                if (
                        not clusters or clusters[-1].f_type != ClusterType.TokenCluster or
                        cluster_index != cluster_token_index
                ):
                    clusters.append(Token(word, cluster_type=ClusterType.TokenCluster))
                    cluster_index = cluster_token_index
                else:
                    clusters[-1].append(word)
                continue

        # Обработка частей речи
        if not word.is_digit:
            if word.pos in (NOUN, PROPN, PRON):
                # Создание нового кластера
                clusters.append(Token(word, cluster_type=ClusterType.PartOfSpeech))
                continue

        # Обработка чисел и слов связок
        if word.is_digit:
            clusters.append(Token(word, cluster_type=ClusterType.Number))
        else:
            clusters.append(Token(word, cluster_type=ClusterType.Null))
        continue

    # Удаление внутренних связей
    for cluster in clusters:
        cluster.remove_connect()

    return clusters, list_node  # Возвращаем список кластеров и список связей между токенами
