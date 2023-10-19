from abc import ABC, abstractmethod, abstractproperty
from inspect import signature, getsource
from typing import Any, Iterable, Callable, List
from types import BuiltinFunctionType, BuiltinMethodType
from rich.console import Console
console = Console()

class FlowError(Exception):
    """Raised when something fails to flow through the pipe."""
    def __init__(self, inner, fn, value):
        self.inner = inner
        self.fn = fn
        self.value = value

    def __repr__(self):
        return f"[red][bold]{type(self.inner).__name__}[/bold]: {self.inner}[/red] on [green]{self.value}[/green] → [blue]{repr(self.fn)}[/blue]"

class Segment(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @property
    def input_types(self): return Any   # TODO we can do better than this for the ones that don't impl. (dea, ig, ag, mc)

    def get_output_types(self, input_example): return type(self(input_example))  # TODO: should be annotated type not string


class FunctionAdapter(Segment):
    def __init__(self, fn):
        self.fn = fn
        self.sig = signature(fn)

    def __call__(self, x): return self.fn(x)

    def __repr__(self):
        if isinstance(self.fn, BuiltinFunctionType) or isinstance(self.fn, BuiltinMethodType):
            return self.fn.__name__
        return getsource(self.fn).strip()

    @property
    def input_types(self):
        return self.sig.parameters.items()

    def get_output_types(self, input_example):
        return self.sig.return_annotation

'''
Dangerous because it executes arbitrary code. Do not use on untrusted input.

Usage: ff(['hello   '])( dea('.strip().upper()') )
instead of having to do  mc('strip'), mc('upper')
(from operator import itemgetter as ig, methodcaller as mc, attrgetter as ag)

todo: make this using macros. macropy?
'''
class DangerousEvalAttr(Segment):
    def __init__(self, expr):
        self.expr = expr

    def __call__(self, x): return eval(f'x{self.expr}')

    def __repr__(self): return self.expr.strip()

    @property
    def input_types(self): return Any


# operator methods: itemgetter, methodcaller, attrgetter
from operator import itemgetter, methodcaller, attrgetter

class ItemGetter(Segment):
    def __init__(self, expr): self.expr = expr
    def __call__(self, x): return itemgetter(self.expr)(x)
    def __repr__(self): return f'[{self.expr}]'

class MethodCaller(Segment):
    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs
    def __call__(self, x): return methodcaller(self.method, *self.args, **self.kwargs)(x)
    def __repr__(self): return f".{self.method}({', '.join(list(self.args) + [f'{k}={v}' for k, v in self.kwargs.items()] )})"

class AttrGetter(Segment):
    def __init__(self, attr): self.attr = attr
    def __call__(self, x): return attrgetter(self.attr)(x)
    def __repr__(self): return f'.{self.attr}'

dea = DangerousEvalAttr
mc = MethodCaller
ig = ItemGetter
ag = AttrGetter

class Vectorize(Segment):
    def __init__(self, seg: Segment): self.seg = seg
    def __call__(self, x_arr): return [self.seg(x) for x in x_arr]
    def __repr__(self): return '...' + repr(self.seg)

class SpreadInto(Segment):
    def __init__(self, seg: Segment): self.seg = seg
    def __call__(self, x_arr): return self.seg(*x_arr)
    def __repr__(self): return '>' + repr(self.seg)

vec = Vectorize
si = SpreadInto

class Compose(Segment):
    def __init__(self, *segs: List[Segment]): self.segs = segs
    def __call__(self, x):
        for f in self.segs:
            try:
                # console.print(f"[green]{type(x).__name__}[/green] ➡️ {repr(f)}")
                x = f(x)    # optm: add vectorizability
            except Exception as e:
                raise FlowError(e, f, x)
        return x
    def __repr__(self): return ' ⮕ '.join(repr(s) for s in self.segs)

class Tee(Segment):
    def __init__(self, *segs: Iterable[Segment]):
        self.funcs = [ingestor(fl) for fl in segs]
    def __call__(self, x):
        return [f(x) for f in self.funcs]
    def __repr__(self):
        return '{ ' + '; '.join(repr(fl) for fl in self.funcs) + ' }'

class LazyTee(Tee):
    def __init__(self, *segs: Iterable[Segment]):
        return super().__init__(self, segs)
    def __call__(self, x):
        return map(lambda f: f(x), self.funcs)

def ingestor(obj: Segment or set or Iterable or Callable):
    if isinstance(obj, Segment):
        return obj
    if isinstance(obj, set):
        return Tee(*[ingestor(f) for f in obj])
    if isinstance(obj, Iterable):
        return Compose(*[ingestor(f) for f in obj])
    if isinstance(obj, Callable):
        return FunctionAdapter(obj)
    else:
        raise NotImplementedError(f"Could not ingest object of type {type(obj)}")

ff_default_eager = True
class Pipeline(Segment):
    def __init__(self, *funcs: List[Callable], eager=ff_default_eager, test_single=False):
        self.pipe = ingestor(funcs)
        self.eager = eager

    def __call__(self, x_arr):
        if self.eager:
            for x in x_arr:
                yield self.pipe(x)
        else:
            return [self.pipe(x) for x in x_arr]
    def __repr__(self):
        return '...' + repr(self.pipe)
rff = Pipeline

def ff(x_arr, eager=ff_default_eager, test_single=False):
    if test_single: x_arr = x_arr[:1]
    def ret(*funcs):
        try:
            pipe = ingestor(funcs)
            return [pipe(x) for x in x_arr] # todo: non-eager version
        except FlowError as fe:
            console.print(fe)
    return ret


if __name__ == '__main__':


    y = ff("hello")
    print(y(ord))



    # dea = DangerousEvalAttr(".strip().split('.')")
    # print(dea('hello.world      .emacs.    '))
    # print(dea)

    # op = MethodCaller('cow')
    # # print(op({ 'pig': 'oink', 'cow': 'moo' }))


    # pipe = ingestor([
    #     dea(".strip().split('.')"),
    #     # vec(lambda s: s.upper())
    #     lambda s: s.upper()
    #     ])
    # print(pipe)
    # print(pipe('hello.world      .emacs.    '))