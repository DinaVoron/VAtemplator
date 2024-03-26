import pickle as pc
from tree import SceneTree, Scene, IntentTemplate, IntentValue

def unpickle(file):
    with open(file, "rb") as f:
        tree = pc.load(f)
    return tree

def topickle(tree, file):
    with open(file, "wb") as f:
        pc.dump(tree, f)

# tree = unpickle("pickle_test.PKL")
# print(tree.get_pretty_nodes())
