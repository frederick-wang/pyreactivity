# reactivity/ref.py

from typing import Dict, Generic, Set, TypeVar, Union, cast

from reactivity.effect.definations import ReactiveEffectDef
from reactivity.effect.utils import (active_effect_stack, track_effects, trigger_effects)
from reactivity.env import DEV
from reactivity.flags import FLAG_OF_REF, REF_VALUE
from reactivity.reactive import reactive
from reactivity.reactive.utils import reactive_reversed_class_map
from reactivity.computed.utils import is_computed_ref

from .definitions import Ref
from .utils import is_ref, unref

T = TypeVar('T')


def track_ref_value(obj: object) -> None:
    track_ref(obj, REF_VALUE)


def trigger_ref_value(obj: object) -> None:
    trigger_ref(obj, REF_VALUE)


def track_ref(obj: object, key: str) -> None:
    if not active_effect_stack:
        return
    if not hasattr(obj, 'deps'):
        return
    if DEV:
        print(f'[{"ComputedRef" if is_computed_ref(obj) else "Ref"}] track: self={obj} at {hex(id(obj))} ({id(obj)})')
    deps: Dict[Union[str, int], Set[ReactiveEffectDef]] = getattr(obj, 'deps')
    if key not in deps:
        deps[key] = set()
    dep = deps[key]
    track_effects(dep)


def trigger_ref(obj: object, key: str) -> None:
    if not hasattr(obj, 'deps'):
        return
    deps_dict: Dict[Union[str, int], Set[ReactiveEffectDef]] = getattr(obj, 'deps')
    if key in deps_dict:
        trigger_effects(deps_dict[key])
    if DEV:
        print(f'[Ref] trigger: self={obj} at {hex(id(obj))} ({id(obj)})')


class RefImpl(Generic[T]):
    __value: T
    deps: Dict[Union[str, int], Set[ReactiveEffectDef]]

    def __init__(self, value: T) -> None:
        if is_ref(value):
            raise TypeError(f'TypeError: Cannot create ref from ref. {value} is already a ref.')
        self.__value = reactive(value)
        self.deps = {}
        setattr(self, FLAG_OF_REF, True)

    @property
    def value(self) -> T:
        track_ref_value(self)
        return self.__value

    @value.setter
    def value(self, value: T) -> None:
        new_value = reactive(value)
        if new_value == self.__value:
            return
        self.__value = new_value
        trigger_ref_value(self)

    def __str__(self) -> str:
        t = type(self.__value)
        if t in reactive_reversed_class_map:
            t = reactive_reversed_class_map[t]
        return f'<Ref[{t.__name__}] value={self.__value}>'


def ref(value: Union[T, Ref[T], None] = None) -> Ref[T]:
    if is_ref(value):
        value = cast(Ref[T], value)
        return value

    value = cast(T, value)
    result = RefImpl(value)
    return cast(Ref[T], result)
