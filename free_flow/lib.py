from typing import TypeVar, Generic, List
from collections.abc import Iterable, Iterator, Callable
from abc import ABC, abstractmethod
from inspect import getsource

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

def dangerous_eval_attr(s):
    '''
    Dangerous because it executes arbitrary code. Do not use on untrusted input.

    Usage: ff(['hello   '])( dea('.strip().upper()') )
    instead of having to do  mc('strip'), mc('upper')
    (from operator import itemgetter as ig, methodcaller as mc, attrgetter as ag)

    todo: make this using macros. macropy?
    '''
    return lambda _: eval(f'_{s}')

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


ff_default_eager = True
def ff(x_arr, eager=ff_default_eager, test_single=False):
    if test_single: x_arr = x_arr[:1]
    def split_composition(funcs, x):
        for f in funcs:
            try:
                x = f(x)
            except Exception as e:
                raise ValueError('got error', e, 'when applying', getsource(f), 'to', x)    # todo: actually helpful errors that tell you what went wrong and what the types/values involved were
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

# same as ff but take the functions as curry first, before the data
def rff(*funcs: List[Callable], eager=ff_default_eager, test_single=False):
    def inner(x_arr):
        return ff(x_arr, eager, test_single)(*funcs)
    return inner

# TODO: print the graph! https://github.com/pydot/pydot
# TODO: make a flatten utility? and a *apply utility? (eg. something turns arr into arr[arr], then i want to apply smt to each thing of the inner

if __name__ == '__main__':
    x = ff('hello', eager=True)(
        Inspect("initial"), T( Print,
                              [ord, lambda x: x**2]), Inspect("after tee"))








    # data pipe:
    # 'hello' --- print --- + --- print ----|

    # ---- process ---- + --- another fn --+
    #                   |                  |
    #                   +---- something ---+--- batch -->


