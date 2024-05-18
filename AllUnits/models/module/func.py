import os


def create_html_content(graph, data):
    text_list  = []
    text_index = 0

    for token in data["doc"]:
        if token.text == "\n":
            text_list.append(("punct", ["<br>"]))
        else:
            if data["status"]["select"]:
                cluster = next((cluster for cluster in data["status"]["select"] if token.i in cluster), None)
                if cluster:
                    index = data["status"]["select"].index(cluster)
                    if not text_list or text_list[-1][0] != "select" or text_index != index:
                        text_list.append(("select", []))
                        text_index = index
                    text_list[-1][1].append(token.text)
                    continue
            if data["status"]["select_related"]:
                cluster = next((cluster for cluster in data["status"]["select_related"] if token.i in cluster), None)
                if cluster:
                    index = data["status"]["select_related"].index(cluster)
                    if not text_list or text_list[-1][0] != "select_related" or text_index != index:
                        text_list.append(("select_related", []))
                        text_index = index
                    text_list[-1][1].append(token.text)
                    continue
            if data["status"]["parent"]:
                cluster = next((cluster for cluster in data["status"]["parent"] if token.i in cluster), None)
                if cluster:
                    index = data["status"]["parent"].index(cluster)
                    if not text_list or text_list[-1][0] != "parent" or text_index != index:
                        text_list.append(("parent", []))
                        text_index = index
                    text_list[-1][1].append(token.text)
                    continue
            if data["status"]["child"]:
                cluster = next((cluster for cluster in data["status"]["child"] if token.i in cluster), None)
                if cluster:
                    index = data["status"]["child"].index(cluster)
                    if not text_list or text_list[-1][0] != "child" or text_index != index:
                        text_list.append(("child", []))
                        text_index = index
                    text_list[-1][1].append(token.text)
                    continue

            if text_list and token.is_punct:
                if text_list[-1][0] in ["select", "select_related", "parent", "child"] or token.lemma_ in '–"':
                    text_list.append(("punct", [token.text]))
                else:
                    text_list[-1][1][-1] += token.text
                continue
            if text_list and text_list[-1][0] == "text":
                text_list[-1][1].append(token.text)
            else:
                text_list.append(("text", [token.text]))

    html = ""
    for text_elem in text_list:
        text = " ".join(text_elem[1])
        if text_elem[0] == "select":
            html += f"<swap class='select'>{text}</swap> "
        elif text_elem[0] == "select_related":
            html += f"<swap class='select_related'>{text}</swap> "
        elif text_elem[0] == "parent":
            html += f"<swap class='parent'>{text}</swap> "
        elif text_elem[0] == "child":
            html += f"<swap class='child'>{text}</swap> "
        elif text_elem[0] == "punct":
            html += f" {text} "
        else:
            html += f"{text} "

    return f"""<p>{html}</p>"""


def create_html_cluster(graph, data):
    data["proc_data"] = ([], [], [], [])

    thead = create_html_cluster_thead()
    tbody = create_html_cluster_tbody(graph, data)

    return f"""
        <table>
            <thead>{thead}</thead>
            <tbody>{tbody}</tbody>
        </table>
    """


def create_html_cluster_thead():
    html = ("<tr>"
            "<th rowspan=\"2\">Индекс</th>"
            "<th rowspan=\"2\">Уровень</th>"
            "<th colspan=\"2\">Лемманизация</th>"
            "<th colspan=\"2\">Связь</th>"
            "<th colspan=\"2\">Тип узла</th>"
            "</tr>"
            
            "<tr>"
            "<th>Текст</th>"
            "<th>Алгоритм: SpaCy</th>"
            "<th>Индекс</th>"
            "<th>Семантическая роль</th>"
            "<th>Интент</th>"
            "<th>Значение</th>"
            "</tr>")
    return html


def create_html_cluster_tbody(graph, data):
    for i, cluster in enumerate(data["clusters"]):
        name, lemma = __get_cluster_view__(graph, data, i)

        if data["clusters"][i].f_intent[0]:
            if name not in data["reference"]:
                data["reference"][name] = set()
            if lemma not in data["reference"][name]:
                data["reference"][name].add(lemma)
        else:
            name = ""
        data["clusters"][i].p_name  = name
        data["clusters"][i].p_lemma = lemma

        if data["status"]["select"]:
            if data["clusters"][i].index in data["status"]["select"]:
                __process_cluster__(data["proc_data"][1], i, data["clusters"][i])
            elif data["clusters"][i].index in data["status"]["parent"]:
                __process_cluster__(data["proc_data"][2], i, data["clusters"][i])
            elif data["clusters"][i].index in data["status"]["child"]:
                __process_cluster__(data["proc_data"][3], i, data["clusters"][i])
        if data["clusters"][i].f_intent[0]:
            __process_cluster__(data["proc_data"][0], i, data["clusters"][i])

    html = ""
    if data["status"]["select"]:
        for data_select in data["proc_data"][1]:
            html += create_html_cluster_select_row(graph, data_select, "select")
        for data_parent in data["proc_data"][2]:
            html += create_html_cluster_select_row(graph, data_parent, "parent")
        for data_child in data["proc_data"][3]:
            html += create_html_cluster_select_row(graph, data_child,  "child")
    for data in data["proc_data"][0]:
        html += create_html_cluster_row(graph, data)

    return html


def __get_cluster_view__(graph, data, index):
    lemma = " ".join(lemma for lemma in data["clusters"][index].lemma)
    if not graph.is_reference_lemma(lemma):
        for key, values in data["reference"].items():
            if lemma in values:
                name = key
                break
        else:
            name = "-".join(f"{text[0:3]}" for text in data["clusters"][index].lemma).title()
    else:
        name = graph.get_reference_lemma(lemma)
    return name, lemma


def __process_cluster__(proc_data, index, cluster):
    for i in range(len(proc_data), 0, -1):
        if proc_data[i - 1][0]["name"] == cluster.p_name:
            j = i - 1
            while j >= 0 and proc_data[j][0]["name"] == cluster.p_name:
                if proc_data[j][0]["lemma"] == cluster.lemma and proc_data[j][0]["intent"] == cluster.f_intent and proc_data[j][0]["value"] == cluster.f_value:
                    __process_cluster_append__(proc_data[j], cluster, index)
                    break
                j -= 1
            else:
                __process_cluster_create__(proc_data, cluster, i, index)
            break
    else:
        __process_cluster_create__(proc_data, cluster, len(proc_data), index)


def __process_cluster_create__(proc_data, cluster, pos, index):
    # Индекс, Уровень, Лемманизация (Текст / SpaCy), Связь (Индекс / Семантическая роль), Тип узла (Интент / Значение)
    dt = {
        "index":         [", ".join(map(str, cluster.index))],
        "layer":         [cluster.layer],
        "name":          cluster.p_name,
        "lemma":         cluster.lemma,
        "connect_index": cluster.connect_index,
        "connect_dep":   cluster.connect_dep,
        "intent":        cluster.f_intent,
        "value":         cluster.f_value,
    }

    proc_data.insert(pos, (dt, [index]))


def __process_cluster_append__(proc_data, cluster, index):
    # Индекс, Уровень, Связь (Индекс / Семантическая роль)
    proc_data[0]["index"].append(', '.join(map(str, cluster.index)))
    proc_data[0]["layer"].append(cluster.layer)
    proc_data[0]["connect_index"].extend(cluster.connect_index)
    proc_data[0]["connect_dep"].extend(cluster.connect_dep)

    proc_data[1].append(index)


def create_html_cluster_row(graph, data):
    html = f"""<tr data-cluster="{data[1]}" ondblclick="select_cluster(this)">"""
    if len(data[0]['index']) >= 5:
        html += f"""<td>{data[0]["index"][:4] + ["…"]}</td>"""
        html += f"""<td>{data[0]["layer"][:4] + ["…"]}</td>"""
    else:
        html += f"""<td>{data[0]["index"]}</td>"""
        html += f"""<td>{data[0]["layer"]}</td>"""
    html += f"""<td>{data[0]["name"]}</td>"""
    html += f"""<td>{"".join(map(lambda lemma: f"<div>{lemma}</div>", data[0]["lemma"]))}</td>"""

    if len(data[0]['connect_index']) >= 5:
        html += f"""<td>{data[0]["connect_index"][:4] + ["…"]}</td>"""
    else:
        html += f"""<td>{data[0]["connect_index"]}</td>"""

    if len(set(data[0]["connect_dep"])) >= 5:
        html += f"""<td>{list(set(data[0]["connect_dep"][:4] + ["…"]))}</td>"""
    else:
        html += f"""<td>{list(set(data[0]["connect_dep"]))}</td>"""

    if data[0]["intent"][1]:
        html += f"""<td onclick="change_cluster_flag('intent', this)">{data[0]["intent"][0]}</td>"""
    else:
        html += f"""<td class="data-disabled">{data[0]["intent"][0]}</td>"""

    if data[0]["value"][1]:
        html += f"""<td onclick="change_cluster_flag('value', this)">{data[0]["value"][0]}</td>"""
    else:
        html += f"""<td class="data-disabled">{data[0]["value"][0]}</td>"""
    html += f"""</tr>"""

    return html


def create_html_cluster_select_row(graph, data, selection):
    html = f"""<tr data-cluster="{data[1]}" ondblclick="select_cluster(this)" class="{selection}">"""
    if len(data[0]['index']) >= 5:
        html += f"""<td>{data[0]["index"][:4] + ["…"]}</td>"""
        html += f"""<td>{data[0]["layer"][:4] + ["…"]}</td>"""
    else:
        html += f"""<td>{data[0]["index"]}</td>"""
        html += f"""<td>{data[0]["layer"]}</td>"""

    if data[0]["intent"][0]:
        if selection == "select":
            html += f"""<td><input type="text" onchange="change_cluster_name('{data[0]['name']}', this.value, '{" ".join(data[0]["lemma"])}')" value="{data[0]['name']}"></td>"""
        else:
            html += f"""<td><input type="text" value="{data[0]['name']}" disabled></td>"""
    else:
        html += f"""<td></td>"""
    html += f"""<td>{"".join(map(lambda lemma: f"<div>{lemma}</div>", data[0]["lemma"]))}</td>"""

    if len(data[0]['connect_index']) >= 5:
        html += f"""<td>{data[0]["connect_index"][:4] + ["…"]}</td>"""
    else:
        html += f"""<td>{data[0]["connect_index"]}</td>"""

    if len(set(data[0]["connect_dep"])) >= 5:
        html += f"""<td>{list(set(data[0]["connect_dep"][:4] + ["…"]))}</td>"""
    else:
        html += f"""<td>{list(set(data[0]["connect_dep"]))}</td>"""

    if data[0]["intent"][1]:
        html += f"""<td onclick="change_cluster_flag('intent', this)">{data[0]["intent"][0]}</td>"""
    else:
        html += f"""<td class="data-disabled">{data[0]["intent"][0]}</td>"""

    if data[0]["value"][1]:
        html += f"""<td onclick="change_cluster_flag('value', this)">{data[0]["value"][0]}</td>"""
    else:
        html += f"""<td class="data-disabled">{data[0]["value"][0]}</td>"""
    html += f"""</tr>"""

    return html


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
        # content = f.read()
        # content = " ".join(line.strip() for line in content.split())
        # return content
        paragraphs = f.readlines()
        content = "\n".join(paragraph.strip() for paragraph in paragraphs)
        return content


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
