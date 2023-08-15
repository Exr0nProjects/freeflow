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





def Inspect(label: str):
    def ret(x):
        print(label + ":", x)
        return x
    return ret

class Segment(ABC):
    def __init__(self):
        self._eager = False
    @property
    def eager(self):
        return self._eager
    @eager.setter
    def eager(self, v: bool):
        self._eager = v


def compose(*funcs: List[Callable]):
    def composition(x):
        for f in funcs:
            x = f(x)
        return x
    return composition

class T(Segment):
    def __init__(self, *funcs_lists: Iterable[Callable or Iterable[Callable]]):
        self.funcs = [compose(*fl) if isinstance(fl, Iterable) else fl for fl in funcs_lists]

    def __call__(self, x):
        if self.eager: return [f(x) for f in self.funcs]
        else: return map(lambda f: f(x), self.funcs)


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

# TODO: print the graph! https://github.com/pydot/pydot

if __name__ == '__main__':
    x = ff('hello', eager=True)(
        Inspect("initial"), T( Print,
                              [ord, lambda x: x**2]), Inspect("after tee"))


