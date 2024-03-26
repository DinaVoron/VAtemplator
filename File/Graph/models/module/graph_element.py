from enum import Enum


class GraphNode:
    def __init__(self, cluster):
        self.p_text   = cluster["lemma"]
        self.f_intent = cluster["f_intent"]
        self.f_value  = cluster["f_value"]

    def is_text(self, text):
        return text == " ".join(self.p_text)

    @property
    def text(self):
        return self.p_text

    @property
    def type(self):
        if not self.f_intent and not self.f_value:
            return "Null"
        if self.f_intent and not self.f_value:
            return "Intent"
        if self.f_intent and self.f_value:
            return "IntentAndMeaning"
        if not self.f_intent and self.f_value:
            return "Meaning"

    @property
    def is_intent(self):
        return self.f_intent

    @property
    def is_meaning(self):
        return self.f_value


class GraphEdge:
    class TypeEdge(Enum):
        Syntax = 0
        Named = 1

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
        return self.f_type == self.TypeEdge.Syntax

    @property
    def is_named(self):
        return self.f_type == self.TypeEdge.Named
