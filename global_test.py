class Test():
    def __init__(self):
        self.a = 1
        self.d = {
            "a": 1
        }

T = Test()
# G = None
G = {
    "asd": 1
}

def a():
    print("a() before")
    # print(T.a)
    # print(T.d)
    print(G)
    # T.a += 1
    # T.d["a"] += 1
    b()
    print("a() after")
    # print(T.a)
    # print(T.d)
    print(G)

def b():
    G["asd"] += 1

def main():
    # global G
    # G = {
    #     "asd": 1
    # }
    a()
    # b()
    a()

if __name__ == "__main__":
    main()