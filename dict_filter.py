from types import SimpleNamespace

class A:
    def __init__(self, name) -> None:
        self.name = name
    
    def __repr__(self):
        return f"'{self.name}'"

a = A("asd")
b = A("bbb")

l = [a, b]

q = list(filter(lambda x: x.name > "a", l))
print(f"{q}")

a = {"name": "asd"}
b = {"name": "bbb"}
l = [a, b, {}]

def get_first_by_name(name, l):
    return list(filter(lambda x: x.get("name") == "asd", l))[0]

print(get_first_by_name("asd", l))

q = dict(((x.get("name"), x) for x in l if x.get("name") is not None))
print(q)

q = [SimpleNamespace(**x) for x in l]
print(q)