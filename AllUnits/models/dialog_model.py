from app import dialog_tree
import tree

def get_scenes():
    res = []
    get_scene(dialog_tree.root, res)
    return res


def get_scene(node, res):
    res.append(node)
    for child in node.children:
        get_scene(child, res)


def get_text_scenes():
    return dialog_tree.get_pretty_nodes()


def get_root():
    return dialog_tree.root

def get_scene_name(cur_scene):
    return cur_scene.name

def find_scene_by_name(name):
    return dialog_tree.to_scene(name)

def get_scene_everything(current_scene):
    stats = [
        current_scene.children,
        current_scene.pass_conditions,
        current_scene.answer,
        current_scene.questions
    ]
    return stats


def add_child(current_scene, child_scene):
    current_scene.add_child(child_scene)

def add_scene():
    pass