class GraphNode:
    def __init__(self, type_, text_, layer_, f_intent_, f_value_):
        self.type_    = str(type_)
        self.text     = str(text_)
        self.layer    = [layer_]
        self.f_intent = f_intent_
        self.f_value  = f_value_

    def __repr__(self):
        return f"{self.text} {self.layer}"

    def is_text(self, text):
        return self.text == str(text)

    @property
    def type(self):
        if self.type_ == "Represent":
            return self.type_
        if self.type_ == "NodeInt":
            if self.f_value:
                return self.type_, "IntentAndMeaning"
            else:
                return self.type_, "Intent"
        if self.type_ == "NodeVal":
            if self.f_value:
                return self.type_, "Meaning"
            else:
                return self.type_, "Null"
        return None

    @property
    def is_intent(self):
        if self.f_intent is not None:
            return self.f_intent
        return False

    @property
    def is_meaning(self):
        if self.f_value is not None:
            return self.f_value
        return False


class GraphEdge:
    def __init__(self, type_, text_):
        self.type  = type_
        self.text  = text_
