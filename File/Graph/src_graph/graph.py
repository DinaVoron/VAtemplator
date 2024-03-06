import networkx as nx
from pyvis.network import Network

from src_graph.graph_element import TokenNode, TypeEdge, GraphNode, GraphEdge
from src_graph.scnd_func import has_common_element


class Graph:
    def __init__(self):
        self.p_graph = nx.DiGraph()
        self.static_index = 1
        self.static_layer = 1

    def visible(self):
        shape = ["triangle", "dot", "dot", "box"]
        color = ["#ffdd00", "#0055cc", "#00aacc", "#7a6a59"]
        size  = [20, 12, 12, 10]

        net = Network(
            height="760px", width="100%", bgcolor="#222222", font_color="white",
            notebook=False, directed=True, select_menu=True, filter_menu=True
        )
        net.set_options(
            """const options = {
              "interaction": {
                "navigationButtons": true
              }
            }"""
        )

        for i in self.p_graph.nodes:
            node = self.p_graph.nodes[i]
            if node['data'].is_intent and not node['data'].is_meaning:
                self._add_node_visible(net, i, node, shape[0], color[0], size[0])
                # net.add_node(
                #     i,
                #     label=" ".join(node['data'].text),
                #     title=f"ID: {i}\n" \
                #           f"L: #{node['layer']}\n" \
                #           f"> {node['data'].text}\n" \
                #           f"> {node['data'].pos}\n" \
                #           f"> {node['data'].type}",
                #     layer=f"#{node['layer']}",
                #     shape=shape[0],
                #     color=color[0],
                #     size=size[0]
                # )
            if node['data'].is_intent and node['data'].is_meaning:
                self._add_node_visible(net, i, node, shape[1], color[1], size[1])
                # net.add_node(
                #     i,
                #     label=" ".join(node['data'].text),
                #     title=f"ID: {i}\n" \
                #           f"L: #{node['layer']}\n" \
                #           f"> {node['data'].text}\n" \
                #           f"> {node['data'].pos}\n" \
                #           f"> {node['data'].type}",
                #     layer=f"#{node['layer']}",
                #     shape=shape[1],
                #     color=color[1],
                #     size=size[1]
                # )
            if not node['data'].is_intent and node['data'].is_meaning:
                self._add_node_visible(net, i, node, shape[2], color[2], size[2])
                # net.add_node(
                #     i,
                #     label=" ".join(node['data'].text),
                #     title=f"ID: {i}\n" \
                #           f"L: #{node['layer']}\n" \
                #           f"> {node['data'].text}\n" \
                #           f"> {node['data'].pos}\n" \
                #           f"> {node['data'].type}",
                #     layer=f"#{node['layer']}",
                #     shape=shape[2],
                #     color=color[2],
                #     size=size[2]
                # )
            if not node['data'].is_intent and not node['data'].is_meaning:
                self._add_node_visible(net, i, node, shape[3], color[3], size[3])
                # net.add_node(
                #     i,
                #     label=" ".join(node['data'].text),
                #     title=f"ID: {i}\n" \
                #           f"L: #{node['layer']}\n" \
                #           f"> {node['data'].text}\n" \
                #           f"> {node['data'].pos}\n" \
                #           f"> {node['data'].type}",
                #     layer=f"#{node['layer']}",
                #     shape=shape[3],
                #     color=color[3],
                #     size=size[3]
                # )

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

    @staticmethod
    def _add_node_visible(net, index, node, shape, color, size):
        net.add_node(
            index,
            label=" ".join(node['data'].text),
            title=f"ID: {index}\n" \
                  f"L: #{node['layer']}\n" \
                  f"> {node['data'].text}\n" \
                  f"> {node['data'].pos}\n" \
                  f"> {node['data'].type}",
            layer=f"#{node['layer']}",
            shape=shape,
            color=color,
            size=size
        )

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
            if token.con_index:
                for j, token_iter in enumerate(tokens):
                    if i != j and token.con_index[0] in token_iter.index: # === 0
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
