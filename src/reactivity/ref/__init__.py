# pyright: reportMissingTypeStubs=false

from typing import Any, Dict, Generic, Set, TypeVar, Union, cast, overload

from reactivity.computed.utils import is_computed_ref
from reactivity.effect.definations import ReactiveEffectDef
from reactivity.effect.utils import track_effects, trigger_effects
from reactivity.effect.vars import active_effect_stack
from reactivity.env import DEBUG
from reactivity.flags import FLAG_OF_REF, REF_VALUE
from reactivity.reactive import reactive
from reactivity.reactive.utils import reactive_reversed_class_map, to_raw

from .definitions import Ref
from .utils import deep_unref, is_ref, unref

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
    if DEBUG:
        print(f'[{"ComputedRef" if is_computed_ref(obj) else "Ref"}] track: self={obj} at {hex(id(obj))} ({id(obj)})')
    deps: Dict[Union[str, int], Set[ReactiveEffectDef[Any]]] = getattr(obj, 'deps')
    if key not in deps:
        deps[key] = set()
    dep = deps[key]
    track_effects(dep)


def trigger_ref(obj: object, key: str) -> None:
    if not hasattr(obj, 'deps'):
        return
    deps_dict: Dict[Union[str, int], Set[ReactiveEffectDef[Any]]] = getattr(obj, 'deps')
    if key in deps_dict:
        trigger_effects(deps_dict[key])
    if DEBUG:
        print(f'[Ref] trigger: self={obj} at {hex(id(obj))} ({id(obj)})')


class RefImpl(Generic[T]):
    __value: T
    deps: Dict[Union[str, int], Set[ReactiveEffectDef[Any]]]

    def __init__(self, value: T) -> None:
        self.__value = to_raw(unref(value))
        self.deps = {}
        setattr(self, FLAG_OF_REF, True)

    @property
    def value(self) -> T:
        track_ref_value(self)
        return reactive(self.__value)

    @value.setter
    def value(self, value: T) -> None:
        old_value = to_raw(self.__value)
        new_value = to_raw(unref(value))
        if new_value == old_value:
            return
        self.__value = new_value
        trigger_ref_value(self)

    def __str__(self) -> str:
        t = type(self.__value)
        if t in reactive_reversed_class_map:
            t = reactive_reversed_class_map[t]
        return f'<Ref[{t.__name__}] value={self.__value}>'


@overload
def ref() -> Ref[Any]:
    ...


@overload
def ref(value: Ref[T]) -> Ref[T]:
    ...


@overload
def ref(value: None) -> Ref[Any]:
    ...


@overload
def ref(value: T) -> Ref[T]:
    ...


def ref(value: Union[Ref[T], T, None] = None) -> Ref[T]:
    if is_ref(value):
        value = cast(Ref[T], value)
        return value

    value = cast(T, value)
    result = RefImpl(value)
    return cast(Ref[T], result)


__all__ = ['is_ref', 'ref', 'unref', 'deep_unref', 'Ref']
