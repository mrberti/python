#%%
import json
import jsonschema

with open("schema.json") as f:
    schema = json.load(f)

obj = {
    "base": "1, 2, 3,",
    "obj": {
        "x": 1,
        # "y": 2,
    }
    # "notIncluded": "asd"
}
obj2 = {
    "qqq": "qweqwe",
    "ddd": "asd"
}
# try:
jsonschema.validate(
    obj,
    schema,
    format_checker=jsonschema.draft202012_format_checker)
# except jsonschema.ValidationError as exc:
#     print(exc)
