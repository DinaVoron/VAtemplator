from tree import *
from testing import *
'''
import importlib
tree_module = input('tree')
importlib.import_module(tree_module)
'''


def main():
    main_scene = Scene(intents=['главный'], int_values=['значение'], name='main', answer=['a', 'intent', 'b'],
                       pass_conditions=[['pass']])
    # 'intent' менять на list intents
    sub1 = Scene(intents=['первый'], int_values=['значение'], name='sub1', pass_conditions=[['one']])
    sub2 = Scene(intents=['второй'], int_values=['значение'], name='sub2', pass_conditions=[['two'], ['three']])
    sub12 = Scene(intents=['первый второй'], int_values=['значение'], name='sub12', pass_conditions=[['four']])
    tree = SceneTree(main_scene)
    main_scene.add_child(sub1)
    main_scene.add_child(sub2)
    sub1.add_child(sub12)
    tree.set_height_tree()
    main_scene.print_scene()
    tree.print_nodes()
    print('---')
    tree.print_pretty_nodes()
    # main_scene.print_answer()

    '''
    tree = ET.parse('info.xml')
    root = tree.getroot()
    to_print = root.findall("intent")
    for tag in to_print:
        print(tag.text)
    '''

    # sg.Window(title="tree_print", layout=[[]], margins=(200, 100)).read()
    # window_tree(tree)

    cur_intents = ['pass', 'one', 'two', 'three']
    next_scene = main_scene.conv_continue(cur_intents)
    # next_scene.print_scene()

    tree.start_conversation()

    # automatic_testing()

    return 0


if __name__ == '__main__':
    main()
