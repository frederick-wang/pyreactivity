# reactivity/effect.py

from typing import Any, Callable, List, Set, TypeVar, Union

from .definations import ReactiveEffectDef
from .utils import cleanup_effect
from .vars import active_effect_stack

T = TypeVar('T')


class ReactiveEffect(ReactiveEffectDef[T]):
    active: bool
    fn: Callable[[], T]
    scheduler: Union[Callable, None]
    computed: Union[Any, None]  # type: ComputedRefImpl[T]
    deps: 'List[Set[ReactiveEffectDef]]'

    def __init__(self, fn: Callable[[], T], scheduler: Union[Callable, None] = None) -> None:
        self.active = True
        self.fn = fn
        self.scheduler = scheduler
        self.computed = None
        self.deps = []

    def run(self) -> T:
        if not self.active:
            return self.fn()
        try:
            active_effect_stack.append(self)
            return self.fn()
        finally:
            if active_effect_stack:
                active_effect_stack.pop()

    def stop(self) -> None:
        cleanup_effect(self)
        self.active = False

    def __call__(self) -> T:
        return self.run()


def effect(update: Callable[[], Any]) -> ReactiveEffect:

    def wrapper():
        e = ReactiveEffect(update)
        e.run()
        return e

    return wrapper()
