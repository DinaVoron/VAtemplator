from app import app, graph
from flask import render_template, request
from models.dialog_model import (get_text_scenes, get_root, get_scene_name,
                                 find_scene_by_name, get_scene_everything,
                                 add_child)


@app.route('/dialog', methods=['get', 'post'])
def editor_dialog():
    all_scenes = get_text_scenes()
    text_scenes = all_scenes.split('\n')
    # Если сцена не выбрана
    if request.values.get('go_to_scene'):
        scene_name = (request.values.get('scene_name'))
        current_scene = find_scene_by_name(scene_name)
        if current_scene is None:
            scene_name = None
            scene_stats = None
        else:
            scene_stats = get_scene_everything(current_scene)
    else:
        current_scene = get_root()
        scene_name = get_scene_name(current_scene)
        scene_stats = get_scene_everything(current_scene)

    html = render_template(
        'editor_dialog.html',
        text_scenes=text_scenes,
        current_scene=current_scene,
        scene_name=scene_name,
        scene_stats=scene_stats,
    )
    return html
