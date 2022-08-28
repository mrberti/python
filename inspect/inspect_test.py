import inspect
import sys
import traceback
from enum import Enum

class e(Enum):
    a = 1
    b = 2
    c = 2

def handle_error(exc, func_name=None):
    print(exc)
    stack = inspect.stack()
    sys_frame = sys._getframe()
    i = 2
    print(f"func_name = {func_name}")
    print(f"filename: {stack[i].filename}")
    print(f"function: {stack[i].function}")
    print(f"context: {stack[i].code_context}")
    print(f"{sys_frame}")

def error_decorator(func):
    def inner_function(*args, **kwargs):
        try:
            self = args[0]
            print(self.q)
            func(*args, **kwargs)
        except ValueError as exc:
            # stack = inspect.currentframe()
            traceback.print_last()
            pass
            # handle_error(exc, func.__name__)
            # print(f"{func.__name__} only takes numbers as the argument")
    return inner_function

class A:
    def __init__(self) -> None:
        self.q = "asd"

    def a(self, x: str):
        self.b(x, 1)
    
    def b(self, x, c):
        try:
            raise ValueError("This is the error text")
        except ValueError as exc:
            handle_error(exc)

    @error_decorator
    def c(self, x, c):
        raise ValueError("This should be decorated")

    def d(self):
        raise Warning("This is a warning")

if __name__ == "__main__":
    a = A()
    # a.a("asd")
    # a.c(1, 2)
    # a.d()
    # print("Ignored :)")
    x = e.c
