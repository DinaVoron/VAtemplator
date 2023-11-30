# import importlib
# STT = importlib.import_module("VTT")
# TTS = importlib.import_module("TTS")


class Scene:
    def __init__(self, intents, int_values, name=None, children=None, pass_conditions=None, answer=None):
        self.name = name
        self.intents = intents
        self.int_values = int_values
        self.children = []
        self.pass_conditions = []
        self.height = 0
        self.answer = answer
        if children is not None:
            for child in children:
                self.add_child(child)
        if pass_conditions is not None:
            for condition in pass_conditions:
                self.add_condition(condition)

    def set_answer(self, answer):
        self.answer = answer

    def set_name(self, name):
        self.name = name

    def set_intents(self, intents):
        self.intents = intents

    def set_int_values(self, int_values):
        self.int_values = int_values

    def add_child(self, node):
        assert isinstance(node, Scene)
        self.children.append(node)

    def add_condition(self, condition):
        assert isinstance(condition, Scene)
        self.pass_conditions.append(condition)

    def print_scene(self):
        print(self.name, self.intents, self.int_values, self.height)

    def print_pretty(self):
        print('---'*self.height, self.name, self.intents, self.int_values, self.height)

    def print_children(self):
        self.print_scene()
        for child in self.children:
            child.print_children()

    def print_pretty_children(self):
        child_counter = 0
        while child_counter < len(self.children) / 2:
            self.children[child_counter].print_pretty_children()
            child_counter += 1
        self.print_pretty()
        while child_counter < len(self.children):
            self.children[child_counter].print_pretty_children()
            child_counter += 1

    def set_height(self, height):
        self.height = height
        return height + 1

    def set_height_all(self, height):
        new_height = self.set_height(height)
        for child in self.children:
            child.set_height_all(new_height)

    def print_answer(self):
        answer = ''
        for ans in self.answer:
            answer += ' ' + ans
        answer += ' '
        print(answer)


class SceneTree:
    def __init__(self, root):
        self.root = root

    def print_nodes(self):
        self.root.print_children()

    def print_pretty_nodes(self):
        self.root.print_pretty_children()

    def set_height_tree(self):
        self.root.set_height_all(0)


def main():
    # TTS.speak('проверка')
    # TTS.speak('текст')
    # print(STT.listen())
    main_scene = Scene(intents=['главный'], int_values=['значение'], name='main', answer=['a', 'intent', 'b'])
    # 'intent' менять на list intents
    sub1 = Scene(intents=['первый'], int_values=['значение'], name='sub1')
    sub2 = Scene(intents=['второй'], int_values=['значение'], name='sub2')
    sub12 = Scene(intents=['первый второй'], int_values=['значение'], name='sub12')
    tree = SceneTree(main_scene)
    main_scene.add_child(sub1)
    main_scene.add_child(sub2)
    sub1.add_child(sub12)
    tree.set_height_tree()
    main_scene.print_scene()
    tree.print_nodes()
    print('---')
    tree.print_pretty_nodes()
    main_scene.print_answer()
    return 0


if __name__ == '__main__':
    main()
