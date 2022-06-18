#%%
import json

paths = [
    "a/b/",
    "a/b/c.txt",
    "a/d.asd",
]

def create_fs_tree(path_list, root_name):
    fs_tree = {
        "name": root_name,
        "children": []
    }

    for path in path_list:
        print(path)
        # Start at root
        current = fs_tree
        is_dir = path.endswith("/")
        leafs = path.split("/")
        print(leafs)
        for leaf in leafs[0:-1]:
            # Search for the item
            for item in current["children"]:
                if item.get("name") == leaf:
                    break
            else:
                # This is executed, when no item has been found
                new_leaf = {
                    "name": leaf,
                    "children": []
                }
                print(f"Created new leaf: {new_leaf}")
                current["children"].append(new_leaf)
                item = current["children"][0]
            # Go to next item
            current = item
        if not is_dir:
            file_name = leafs[-1]
            new_leaf = {
                "name": file_name,
                "file": ".txt"
            }
            current["children"].append(new_leaf)
    return fs_tree

fs_tree = create_fs_tree(paths, "this_is_my_root")
print(json.dumps(fs_tree, indent=2))

