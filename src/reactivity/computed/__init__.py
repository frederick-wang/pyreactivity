# reactivity/computed.py

from typing import Callable, Dict, Generic, Set, TypeVar, Union, cast

from reactivity.effect import ReactiveEffect
from reactivity.flags import (FLAG_OF_COMPUTED_REF, FLAG_OF_READONLY, FLAG_OF_REF)
from reactivity.ref import track_ref_value, trigger_ref_value
from reactivity.reactive.utils import reactive_reversed_class_map

from .definitions import ComputedRef
from .utils import is_computed_ref

T = TypeVar('T')


class ComputedRefImpl(Generic[T]):
    __value: Union[T, None]
    deps: Dict[Union[str, int], Set[ReactiveEffect]]
    effect: ReactiveEffect[T]
    _dirty: bool
    _cacheable: bool

    def __init__(self, getter: Callable[[], T]) -> None:
        self.__value = None
        self._dirty = True
        self._cacheable = True
        self.deps = {}

        def scheduler():
            if not self._dirty:
                self._dirty = True
                trigger_ref_value(self)

        self.effect = ReactiveEffect(getter, scheduler)
        self.effect.computed = self
        self.effect.active = self._cacheable
        setattr(self, FLAG_OF_COMPUTED_REF, True)
        setattr(self, FLAG_OF_REF, True)
        setattr(self, FLAG_OF_READONLY, True)

    @property
    def value(self) -> T:
        track_ref_value(self)
        if self._dirty:
            self._dirty = False
            self.__value = self.effect.run()
        return cast(T, self.__value)

    def __str__(self) -> str:
        t = type(self.__value)
        if t in reactive_reversed_class_map:
            t = reactive_reversed_class_map[t]
        return f'<ComputedRef[{t.__name__}] value={self.__value}>'


def computed(getter: Callable[[], T]) -> ComputedRef[T]:
    result = ComputedRefImpl(getter)
    return cast(ComputedRef[T], result)
