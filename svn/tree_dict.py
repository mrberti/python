#%%
import json
from pathlib import Path

paths = [
    "a/b/",
    "a/b/c.txt",
    "a/d.html",
    "q.tar.gz",
    "q/b",
]

def create_fs_tree(path_list):
    fs_tree = []

    for path in path_list:
        print(path)
        # Start at root
        current = fs_tree
        is_dir = path.endswith("/")
        leafs = path.split("/")
        print(leafs)
        for index, leaf in enumerate(leafs[0:-1]):
            print(index, leaf)
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
                print(f"Created new leaf: {new_leaf}")
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

def tree_to_list(fs_tree, reduce=False):
    # print(fs_tree)
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

fs_tree = create_fs_tree(paths)
print(json.dumps(fs_tree, indent=2))
fs_list = tree_to_list(fs_tree, reduce=False)
fs_list_reduced = tree_to_list(fs_tree, reduce=True)
print(json.dumps(fs_list, indent=2))
print(json.dumps(fs_list_reduced, indent=2))