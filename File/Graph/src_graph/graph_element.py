from enum import Enum


class TokenNode(Enum):
    Null = 0
    Intent = 1
    IntentAndMeaning = 2
    Meaning = 3


class TypeEdge(Enum):
    Syntax = 0
    Named = 1


class GraphNode:
    def __init__(self, token):
        self.p_text = token.lemma
        self.p_pos  = token.pos
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
