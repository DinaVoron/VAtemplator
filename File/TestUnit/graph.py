class Node(object):
    def __init__(self, id, text, type):
        self.id = id
        self.text = text
        self.type = type

    def id(self):
        return self.id

    def text(self):
        return self.text


class Link(object):
    def __init__(self, start, end, type):
        self.start = start
        self.end = end
        self.type = type

    def end(self):
        return self.end

    def start(self):
        print(self.start)
        return self.start

def graph_testing(smgraph):
    for i in range(len(smgraph)):
        next = smgraph[i].end
        for j in range(i+1, len(smgraph)):
            if smgraph[j].start == next:
                print("Не хотите добавить вопрос с такими интентами?")
                print(
                    nodes[smgraph[i].start - 1].text
                    + " "
                    + nodes[smgraph[i].end - 1].text
                    + " "
                    + nodes[smgraph[j].end - 1].text)


n1 = Node(1, "Балл", "intent")
n2 = Node(2, "Специальность", "intent")
n3 = Node(3, "2020", "value")
n4 = Node(4, "Год", "intent")
n5 = Node(5, "Программная инженерия", "value")
n6 = Node(6, "210", "value")

nodes = [
    n1, n2, n3, n4, n5, n6
]

link1 = Link(2,5, "DET")
link2 = Link(5, 4, "ATTR")
link3 = Link(4, 3, "DET")
link4 = Link(3, 1, "ATTR")
link5 = Link(1, 6, "DET")

graph = [
    link1, link2, link3, link4, link5
]

graph_testing(graph)





