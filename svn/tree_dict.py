#%%
import re
from pathlib import Path
import json

from svn_tools import *

paths = [
    "a/b/",
    "a/b/c.txt",
    "a/b/c.txt",
    "a/d.html",
    "q.tar.gz",
    "q/b",
]

def create_fs_tree(path_list):
    fs_tree = []

    # Make sure, that no doubled entries exist
    for path in set(path_list):
        # Start at root
        current = fs_tree
        is_dir = path.endswith("/")
        leafs = path.split("/")
        for index, leaf in enumerate(leafs[0:-1]):
            # Search for the item
            found_leaf = False
            for item in current:
                if item.get("name") == leaf:
                    found_leaf = True
                    break
            if not found_leaf:
                # This is executed, when no item has been found
                new_leaf = {
                    "id": "/".join(leafs[0:index+1]) + "/",
                    "name": leaf,
                    "children": []
                }
                current.append(new_leaf)
                item = new_leaf
            # Go to next item
            current = item["children"]
        if not is_dir:
            file_name = leafs[-1]
            file_path = Path(path)
            file_extension = "".join(file_path.suffixes)
            # Delete leading '.'
            file_extension = file_extension[1:]
            new_leaf = {
                "id": path,
                "name": file_name,
                "file": file_extension
            }
            current.append(new_leaf)
    return fs_tree

def filter_tree(fs_tree, reg_ex):
    fs_list = tree_to_list(fs_tree, reduce=True)
    filtered_list = filter_list(fs_list, reg_ex)
    filtered_fs = create_fs_tree(filtered_list)
    return filtered_fs

def filter_list(fs_list, reg_ex):
    if not isinstance(reg_ex, re.Pattern):
        reg_ex = re.compile(reg_ex)
    filtered_list = list(filter(lambda x: reg_ex.search(x), fs_list))
    return filtered_list

def tree_to_list(fs_tree, reduce=False):
    fs_list = []
    for item in fs_tree:
        if "children" in item:
            this = {}
            for key, value in item.items():
                if key == "children":
                    continue
                this[key] = value
            fs_list += [this] + tree_to_list(item["children"])
        else:
            fs_list += [item]
    if reduce:
        fs_list = sorted([x["id"] for x in fs_list])
    else:
        fs_list = sorted(fs_list, key=lambda d: d['id']) 
    return fs_list

def get_files_local(root_dir):
    files_list = []
    for root, dirs, files in os.walk(root_dir, followlinks=False):
        if ".svn" in root:
            continue
        files_list.append(f"{root}/")
        files_list += [f"{root}/{file}" for file in files]
    return files_list

#%%
if __name__ == "__main__":
    repo = "svn+ssh://simon@pi/home/simon/svn/test"
    paths = get_files_simple(repo, revision=8)
    print(paths)
    paths = get_files_local(wc_path)
    print(paths)
    # fs_tree = create_fs_tree(paths)
    # print(json.dumps(fs_tree, indent=2))
    # fs_list = tree_to_list(fs_tree, reduce=False)
    # fs_list_reduced = tree_to_list(fs_tree, reduce=True)
    # print(json.dumps(fs_list, indent=2))
    # print(json.dumps(fs_list_reduced, indent=2))
    # filter_ = r".*/711.*txt$"
    # filtered = filter_tree(fs_tree, filter_)
    # filtered = filter_list(fs_list_reduced, filter_)
    # print(json.dumps(filtered, indent=2))
