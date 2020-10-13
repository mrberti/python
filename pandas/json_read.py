#%%
import os
import json
import pandas as pd

file_path = os.path.dirname(__file__) + "/data.json"
with open(file_path, "r") as f:
    file_data = f.read()
json_data = json.loads(file_data)
# data = pd.read_json(file_path, orient="split")
data2 = pd.json_normalize(json_data, "data")
others = pd.json_normalize(json_data, "others")

# print(data)
print(data2)
print(others)
# %%
