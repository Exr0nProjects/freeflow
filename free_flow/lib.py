from typing import TypeVar, Generic, List
from collections.abc import Iterable, Iterator, Callable
from abc import ABC, abstractmethod

T = TypeVar('T')
W = TypeVar('W')

class Segment(ABC):
    @abstractmethod
    def apply(input): pass

# def map(fn: Callable[[T], W]):
#     pass

def Noop(x):
    return x

def Ret1(x):
    return 1

def Print(x):
    print(x)
    return x

def SimpleTee(*funcs):
    def fn(x):
        print("teeing!", x)
        return map(lambda f: f(x), funcs)
    return fn

def compose(*funcs: List[Callable]):
    def composition(x):
        for f in funcs:
            x = f(x)
        return x
    return composition

def ff(x_arr):
    def split_composition(funcs, x):
        for f in funcs:
            x = f(x)
        return x
    def gen(*funcs: List[Callable]):
        for x in x_arr:
            yield split_composition(funcs, x)
    return gen

def ff_eager(x_arr):
    def split_composition(funcs, x):
        for f in funcs:
            x = f(x)
        return x
    def gen(*funcs: List[Callable]):
        for x in x_arr:
            yield split_composition(funcs, x)
    return gen

# def ff(input: Iterable[T]):
#     class Curried(Iterable):
#         def __init__(self, *segments: List[Segment]):
#             self.segments = segments
#             # todo: type checking: https://stackoverflow.com/a/50181256
#             self.composition = compose(segments)
#         def __iter__(self):
#             yield from self.composition(input)
#     return Curried

if __name__ == '__main__':
    # comp = compose(Ret1, print)
    # print(comp("hewo"))
    g = [*ff('hello!')(SimpleTee(Print, compose(Ret1, Print)))]
    print(g)
    # print(list(ff('hello!')(Noop)))
    # ff('hello!')(Print, SimpleTee(compose(Ret1, print),
    #                               Print))

# want to allow this
# -----+---->
#      +---->
#

