from typing import TypeVar, Union, cast

from reactivity.flags import FLAG_OF_REF
from reactivity.reactive.utils import to_raw

from .definitions import Ref

T = TypeVar('T')


def is_ref(obj: object) -> bool:
    return hasattr(obj, FLAG_OF_REF)


def unref(obj: 'Union[Ref[T], T]') -> T:
    if is_ref(obj):
        obj = cast(Ref[T], obj)
        return to_raw(obj.value)
    obj = cast(T, obj)
    return obj
