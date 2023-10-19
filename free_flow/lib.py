from typing import TypeVar, Generic, List
from collections.abc import Iterable, Iterator, Callable
from inspect import getsource, signature

from rich.console import Console
console = Console()

ff_default_eager = True

T = TypeVar('T')
W = TypeVar('W')


def Noop(x):
    return x

def Ret1(x):
    return 1

def Print(x):
    console.print(x)
    return x



def Inspect(label: str):
    def ret(x):
        console.print(label + ":", x, style="bold")
        return x
    ret.__qualname__ = "Inspect"
    return ret


from segments import ff
# TODO: print the graph! https://github.com/pydot/pydot
# TODO: make a flatten utility?

if __name__ == '__main__':
    x = ff('hello', eager=True)(
        Inspect("initial"), T( Print,
                              [ord, lambda x: x**2 ]), Inspect("after tee"))

    # data pipe:
    # 'hello' --- print --- + --- print ----|

    # ---- process ---- + --- another fn --+
    #                   |                  |
    #                   +---- something ---+--- batch -->


