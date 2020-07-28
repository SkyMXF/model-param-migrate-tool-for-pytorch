import os
import glob
import collections

import torch
import eel

MODEL_DIR = os.path.join("models")
src_params_tree = None
aim_params_tree = None
migration_entry_list = []
migration_view_list = []
id_for_tree_node = 0
src_model_path = None
aim_model_path = None

def load_model(model_path):

    model_dict = torch.load(model_path)
    if (not isinstance(model_dict, collections.OrderedDict)) and (not isinstance(model_dict, dict)):    # this .pth may be saved as a nn.module but not dict:
        raise Exception(".pth must save an dict or OrderedDict")

    return model_dict

def load_full_module(model_path):
    return torch.load(model_path)

def save_model(model, model_path):
    torch.save(model, model_path)

def get_params_tree(model_dict):
    """return a dict like:
    [
        {
            "name": "encoder",
            "id": 0,
            "leaf": False,
            "shape": None,
            "father": None,
            "children": [
                "name": "conv1",
                "id": 1,
                "leaf": False,
                "shape": None,
                "father": ...,  # pointer to father node dict
                "children": [...]
            ]
        },
        {...},
        ...
    ]
    - one dict for every node, list means edges of tree
    """
    tree_list = []
    node_id = 0
    for arg_name in model_dict.keys():
        # arg_name form like "encoder.layer0.conv0.weights"
        nodes = str(arg_name).split(".")
        now_node_list = tree_list
        now_father_node = None
        for depth_idx in range(len(nodes)):
            node_name = nodes[depth_idx]
            # enter or build tree node until leaf node
            aim_node_idx = -1
            for node_idx in range(len(now_node_list)):
                # find aim node dict
                if now_node_list[node_idx]["name"] == node_name:
                    aim_node_idx = node_idx
                    break
            if aim_node_idx < 0:
                # did not find node, build it
                now_node_list.append({
                    "name": node_name,
                    "id": node_id,
                    "leaf": False,
                    "shape": None,
                    "father": now_father_node,
                    "children": []
                })
                node_id += 1
                aim_node_idx = len(now_node_list) - 1
                
            if depth_idx == len(nodes) - 1:
                # leaf node
                now_node_list[aim_node_idx]["leaf"] = True
                now_node_list[aim_node_idx]["shape"] = model_dict[arg_name].shape
            else:
                # branch node, enter
                now_father_node = now_node_list[aim_node_idx]
                now_node_list = now_node_list[aim_node_idx]["children"]
    
    return tree_list

def get_root_node(tree_list:list):
    """list of tree -> an abstract root node(dict)
    """
    return {
        "name": "",
        "id": -1,
        "leaf": False,
        "shape": None,
        "father": None,
        "children": tree_list
    }

def print_tree(tree_list, space_num=0):
    for node in tree_list:
        print(space_num * " " + "-%s, %d, isLeaf:%s, father:%s"%(node["name"], node["id"], str(node["leaf"]), node["father"]["name"]))
        print_tree(node["children"], space_num+1)

@eel.expose
def eel_get_model_list():
    model_path_list = glob.glob(os.path.join(MODEL_DIR, "*"))
    for model_idx in range(len(model_path_list)):
        model_path_list[model_idx] = os.path.basename(model_path_list[model_idx])
    return model_path_list

@eel.expose
def load_src_tree(model_name):
    global src_params_tree, src_model_path
    src_model_path = os.path.join(MODEL_DIR, model_name)
    try:
        src_params_tree = get_params_tree(load_model(src_model_path))
    except Exception as e:
        return ["FAILED to load src model '%s'. Detail: %s. HINT: If this .pth is saved by 'torch.save(model, path)', try to convert it into 'torch.save(model.state_dict(), path)'"%(model_name, str(e)), []]
    
    # convert to layui tree struct
    global id_for_tree_node
    id_for_tree_node = 0
    list_for_view = []
    parse_tree_for_view(src_params_tree, list_for_view)

    return ["", list_for_view]

@eel.expose
def load_aim_tree(model_name):
    global aim_params_tree, aim_model_path
    aim_model_path = os.path.join(MODEL_DIR, model_name)
    try:
        aim_params_tree = get_params_tree(load_model(aim_model_path))
    except Exception as e:
        return ["FAILED to load aim model '%s'. Detail: %s. HINT: If this .pth is saved by 'torch.save(model, path)', try to convert it into 'torch.save(model.state_dict(), path)'"%(model_name, str(e)), []]
    
    # convert to layui tree struct
    global id_for_tree_node
    id_for_tree_node = 0
    list_for_view = []
    parse_tree_for_view(aim_params_tree, list_for_view)

    return ["", list_for_view]

def parse_tree_for_view(now_node_list:list, now_view_list:list):
    global id_for_tree_node
    for node in now_node_list:
        now_view_list.append({"title": node["name"], "id": id_for_tree_node, "children": []})
        id_for_tree_node += 1
        if node["leaf"]:
            # leaf node
            now_view_list[-1]["title"] += str(list(node["shape"]))
        else:
            # branch node
            parse_tree_for_view(node["children"], now_view_list[-1]["children"])

# migration part
@eel.expose
def add_migration_entry(src_sub_view_node:dict, aim_sub_view_node:dict):

    global src_params_tree, aim_params_tree
    
    # find sub node in real tree struct
    src_sub_real_node = find_real_node(src_sub_view_node["id"], src_params_tree)
    aim_sub_real_node = find_real_node(aim_sub_view_node["id"], aim_params_tree)

    # find all matched leaf node
    matched_leafs = []
    find_match_node(src_sub_real_node, aim_sub_real_node, matched_leafs)
    if len(matched_leafs) <= 0:
        return ["Operation FAILED: Could not find any matched nodes. HINT: Only those nodes with the same shape(or sub nodes with the same name and shape) will be matched.", migration_view_list]

    # add into migrate list
    for match_tuple in matched_leafs:
        # get node path in the whole tree
        src_node_path, src_node_str_path = get_node_path(match_tuple[0])
        aim_node_path, aim_node_str_path = get_node_path(match_tuple[1])

        # append
        migration_entry_list.append({"src": match_tuple[0], "src_path": src_node_str_path, "aim": match_tuple[1], "aim_path": aim_node_str_path})
        migration_view_list.append({"src": src_node_str_path, "aim": aim_node_str_path, "shape": str(list(match_tuple[0]["shape"]))})

    return ["", migration_view_list]

def find_real_node(view_node_id: int, now_real_tree:list):
    for node_idx_in_layer in range(len(now_real_tree)):
        if now_real_tree[node_idx_in_layer]["id"] == view_node_id:
            # successfully find real node
            return now_real_tree[node_idx_in_layer]
        elif now_real_tree[node_idx_in_layer]["id"] > view_node_id:
            # try to find in brother node
            return find_real_node(view_node_id, now_real_tree[node_idx_in_layer - 1]["children"])
    # try to find in last node
    return find_real_node(view_node_id, now_real_tree[-1]["children"])

def find_match_node(src_node:dict, aim_node:dict, match_leaf_list:list):
    if src_node["leaf"] and aim_node["leaf"]:
        # reach leaf node, compare their name and shape
        if src_node["name"] == aim_node["name"] and src_node["shape"] == aim_node["shape"]:
            match_leaf_list.append((src_node, aim_node))
    elif (not src_node["leaf"]) and (not aim_node["leaf"]):
        # both branch node in src and aim
        for src_sub_node in src_node["children"]:
            for aim_sub_node in aim_node["children"]:
                # try to find deeper match nodes if nodes have the same name in src and aim
                if src_sub_node["name"] == aim_sub_node["name"]:
                    find_match_node(src_sub_node, aim_sub_node, match_leaf_list)

def get_node_path(node:dict):
    now_node = node
    path_list = [node]
    str_path = node["name"]
    while now_node["father"]:
        now_node = now_node["father"]
        path_list.append(now_node)
        str_path = now_node["name"] + "." + str_path
    
    return path_list.reverse(), str_path

@eel.expose
def remove_migration_entry(rm_entry_idxs:list):
    rm_entry_idxs.sort()
    for rm_num in range(len(rm_entry_idxs)):
        migration_entry_list.pop(rm_entry_idxs[rm_num] - rm_num)
        migration_view_list.pop(rm_entry_idxs[rm_num] - rm_num)
    
    return ["", migration_view_list]

@eel.expose
def apply_migration():
    # load model
    global src_model_path, aim_model_path
    src_model_dict = load_model(src_model_path)
    aim_model_dict = load_model(aim_model_path)

    message = ""
    
    # apply migration
    global migration_entry_list, migration_view_list
    entry_copy = migration_entry_list[:]
    view_copy = migration_view_list[:]
    try:
        # apply all entrys
        entry_idx = 0
        migrate_log = "src_param,aim_param,shape\n"
        for migrate_entry in migration_entry_list:
            apply_entry(src_model_dict, aim_model_dict, migrate_entry)
            migrate_log += "\"%s\",\"%s\",\"%s\"\n"%(migrate_entry["src_path"], migrate_entry["aim_path"], str(list(migrate_entry["src"]["shape"])))
            entry_idx += 1

        # save new model
        save_model(aim_model_dict, aim_model_path + ".migrated")
        with open(aim_model_path + ".csv", "w") as f:
            print(migrate_log, file=f)
        migration_entry_list = []
        migration_view_list = []
        message = "Migration succeeded. Saved new model params to %s, remember to remove the '.migrated' in the file name before use it."%(aim_model_path + ".migrated")
    except Exception as e:
        message = "Migration FAILED: catch an error when applying entry %s->%s"%(migration_entry_list[entry_idx]["src_path"], migration_entry_list[entry_idx]["aim_path"]) + str(e)
        # restore migration entry
        migration_entry_list = entry_copy
        migration_view_list = view_copy
    finally:
        return [message, migration_view_list]

def apply_entry(src_model_dict, aim_model_dict, migrate_entry):
    aim_model_dict[migrate_entry["aim_path"]] = src_model_dict[migrate_entry["src_path"]]

@eel.expose
def refresh_all_data():
    global migration_entry_list, migration_view_list, src_params_tree, aim_params_tree, src_model_path, aim_model_path
    migration_entry_list = []
    migration_view_list = []
    src_params_tree = None
    aim_params_tree = None
    src_model_path = None
    aim_model_path = None

def main():
    eel.init("html_ui")
    options = {
        "mode": None, #or "chrome-app" to open chrome
        "port": 8000,
        "chromeFlags": ["-kiosk"]
    }
    print("Start a server on http://localhost:8000/main.html ...")
    eel.start("main.html", options=options, suppress_error=True)

if __name__ == "__main__":
    main()