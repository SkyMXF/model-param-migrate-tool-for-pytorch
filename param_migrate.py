import os
import glob

import torch
import eel

LEAF_NODE_KEY = "PT_LEAF"
MODEL_DIR = os.path.join("..", "pretrained")

def load_model(model_path):
    return torch.load(model_path)

def get_params_tree(model_dict):
    """return a dict like:
    {
        "encoder": {
            "layer0": {
                "conv0": {...}
            },
            "layer1": {...}
        },
        "decoder": {...}
    }
    - Leaf node will have only one key named by LEAF_NODE_KEY, and its value is its shape(type: str)
    """
    tree_dict = {}
    for arg_name in model_dict.keys():
        # arg_name form like "encoder.layer0.conv0.weights"
        levels = str(arg_name).split(".")
        now_level_dict = tree_dict
        for level_name in levels:
            # enter or build tree level until leaf node
            if level_name in now_level_dict.keys():
                # find this level, enter
                now_level_dict = now_level_dict[level_name]
            else:
                # did not find this level, build it and then enter
                now_level_dict[level_name] = {}
                now_level_dict = now_level_dict[level_name]
        
        # get tensor shape for leaf node
        now_level_dict[LEAF_NODE_KEY] = str(list(model_dict[arg_name].shape))
    
    return tree_dict

@eel.expose
def eel_get_model_list():
    model_path_list = glob.glob(os.path.join(MODEL_DIR, "*"))
    for model_idx in range(len(model_path_list)):
        model_path_list[model_idx] = os.path.basename(model_path_list[model_idx])
    return model_path_list

id_for_tree_node = 0
@eel.expose
def eel_get_tree_view(model_name):
    model_path = os.path.join(MODEL_DIR, model_name)
    tree_dict = get_params_tree(load_model(model_path))

    # convert to layui tree struct
    global id_for_tree_node
    id_for_tree_node = 0
    list_for_view = []
    parse_dict_tree(tree_dict, list_for_view)

    return list_for_view

def parse_dict_tree(now_dict:dict, now_list:list, upper_list=None):
    global id_for_tree_node
    for k in now_dict.keys():
        if k == LEAF_NODE_KEY:
            # reach leaf node, add shape info to title
            upper_list[-1]["title"] += now_dict[LEAF_NODE_KEY]
            break
        now_list.append(
            {"title": k, "id": id_for_tree_node, "children": []}
        )
        id_for_tree_node += 1
        parse_dict_tree(now_dict[k], now_list=now_list[-1]["children"], upper_list=now_list)

def main():
    eel.init("html_ui")
    options = {
        "mode": None, #or "chrome-app" to open chrome
        "port": 8000,
        "chromeFlags": ["-kiosk"]
    }
    eel.start("main.html", options=options, suppress_error=True)

if __name__ == "__main__":
    main()