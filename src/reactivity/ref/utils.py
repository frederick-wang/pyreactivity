# pyright: reportMissingTypeStubs=false

from typing import Any, Dict, Iterable, TypeVar, Union, cast, overload

from reactivity.flags import FLAG_OF_REF

from .definitions import Ref

T = TypeVar('T')


def is_ref(obj: object) -> bool:
    return hasattr(obj, FLAG_OF_REF)


@overload
def unref(obj: Ref[T]) -> T:
    ...


@overload
def unref(obj: T) -> T:
    ...


def unref(obj: Union[Ref[T], T]) -> T:
    if is_ref(obj):
        obj = cast(Ref[T], obj)
        return obj.value
    obj = cast(T, obj)
    return obj


@overload
def deep_unref(obj: Ref[T]) -> T:
    ...


@overload
def deep_unref(obj: T) -> T:
    ...


def deep_unref(obj: 'Union[Ref[T], T]') -> T:
    if is_ref(obj):
        obj = cast(Ref[T], obj)
        v = obj.value
    else:
        v = cast(T, obj)

    if isinstance(v, dict):
        v = cast(Dict[Any, Any], v)
        return cast(T, {k: deep_unref(v) for k, v in v.items()})
    elif isinstance(v, list):
        v = cast(Iterable[Any], v)
        return cast(T, [deep_unref(i) for i in v])
    elif isinstance(v, tuple):
        v = cast(Iterable[Any], v)
        return cast(T, tuple(deep_unref(i) for i in v))
    elif isinstance(v, set):
        v = cast(Iterable[Any], v)
        return cast(T, {deep_unref(i) for i in v})
    elif isinstance(v, frozenset):
        v = cast(Iterable[Any], v)
        return cast(T, frozenset(deep_unref(i) for i in v))
    return v
