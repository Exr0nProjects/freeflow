from typing import TypeVar, Generic, List
from collections.abc import Iterable, Iterator, Callable
from abc import ABC, abstractmethod

T = TypeVar('T')
W = TypeVar('W')

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
        return map(lambda f: f(x), funcs)
    return fn

def EagerTee(*funcs):
    def fn(x):
        return [f(x) for f in funcs]
    return fn



class Segment(ABC):
    def __init__(self):
        self._eager = False
    @property
    def eager(self):
        return self._eager
    @eager.setter
    def eager(self, v: bool):
        self._eager = v

class Tee(Segment):
    def __init__(self, *funcs):
        self.funcs = funcs
        super().__init__()

    def __call__(self, x):
        if self.eager: return [f(x) for f in self.funcs]
        else: return map(lambda f: f(x), self.funcs)


def compose(*funcs: List[Callable]):
    def composition(x):
        for f in funcs:
            x = f(x)
        return x
    return composition

def ff(x_arr, eager=False):
    def split_composition(funcs, x):
        for f in funcs:
            x = f(x)
        return x
    def gen(*funcs: List[Callable]):
        for x in x_arr:
            yield split_composition(funcs, x)
    def gen_eager(*funcs: List[Callable]):
        for f in funcs:
            if isinstance(f, Segment):
                f.eager = True
        return [split_composition(funcs, x) for x in x_arr]
    return gen_eager if eager else gen

if __name__ == '__main__':

    x = ff('hello', eager=False)(Tee(Print, compose(Ret1, Print)))
    print([[*y] for y in x])

# want to allow this
# -----+---->
#      +---->
#

