# pyright: reportMissingTypeStubs=false

from typing import Any, Dict, Iterable, Set, TypeVar, Union, cast

from reactivity.effect.definations import ReactiveEffectDef
from reactivity.effect.utils import track_effects, trigger_effects
from reactivity.effect.vars import active_effect_stack
from reactivity.env import DEBUG
from reactivity.flags import FLAG_OF_REACTIVE, REACTIVITY_VALUE

T = TypeVar('T')

reactive_class_map: Dict[type, type] = {}
reactive_reversed_class_map: Dict[type, type] = {}
reactive_deps_map: 'Dict[int, Dict[Union[str, int], Set[ReactiveEffectDef[Any]]]]' = {}

__global_reactive_object_map: Dict[int, object] = {}
__global_original_object_map: Dict[int, object] = {}

__marked_raw_set: Set[int] = set()


def is_reactive(obj: object) -> bool:
    return hasattr(obj, FLAG_OF_REACTIVE)


def is_reactive_multable_sequence(obj: object) -> bool:
    return hasattr(obj, '__setitem__') and hasattr(obj, '__getitem__') and is_reactive(obj)


def __get_reactive_subscribers(obj: object, key: Union[str, int]) -> Set[ReactiveEffectDef[Any]]:
    obj_id = id(obj)
    if obj_id not in reactive_deps_map:
        reactive_deps_map[obj_id] = {}
    if key not in reactive_deps_map[obj_id]:
        reactive_deps_map[obj_id][key] = set()
    return reactive_deps_map[obj_id][key]


def track_reactive(obj: object, key: str) -> None:
    if not active_effect_stack:
        return
    deps = __get_reactive_subscribers(obj, key)
    track_effects(deps)


def track_reactive_value(obj: object) -> None:
    track_reactive(obj, REACTIVITY_VALUE)


def trigger_reactive(obj: object, key: str) -> None:
    subscribers = __get_reactive_subscribers(obj, key)
    trigger_effects(subscribers)


def trigger_reactive_value(obj: object) -> None:
    trigger_reactive(obj, REACTIVITY_VALUE)


def is_in_global_reactive_object_map(original: object) -> bool:
    return id(original) in __global_reactive_object_map


def is_in_global_original_object_map(observed: object) -> bool:
    return id(observed) in __global_original_object_map


def get_global_reactive_obj(original: T) -> T:
    return cast(T, __global_reactive_object_map[id(original)])


def to_raw(observed: T) -> T:
    observed_id = id(observed)
    if observed_id in __global_original_object_map:
        return cast(T, __global_original_object_map[observed_id])
    return observed


def deep_to_raw(observed: T) -> T:
    '''Recursively convert a reactive object to a plain python object.
    
    **Note:**
    
    The object returned is **not guaranteed** to be the original object.
    
    The only guarantee is that the object returned must be a plain python object.

    Args:
        observed (T): The object to be converted.

    Returns:
        T: The converted object, which must be a plain python object.
    '''
    if isinstance(observed, dict):
        observed_dict = cast(Dict[Any, Any], observed)
        return cast(T, {k: deep_to_raw(v) for k, v in observed_dict.items()})
    elif isinstance(observed, list):
        observed_list = cast(Iterable[Any], observed)
        return cast(T, [deep_to_raw(v) for v in observed_list])
    elif isinstance(observed, tuple):
        observed_tuple = cast(Iterable[Any], observed)
        return cast(T, tuple(deep_to_raw(v) for v in observed_tuple))
    elif isinstance(observed, set):
        observed_set = cast(Iterable[Any], observed)
        return cast(T, {deep_to_raw(v) for v in observed_set})
    elif isinstance(observed, frozenset):
        observed_frozenset = cast(Iterable[Any], observed)
        return cast(T, frozenset(deep_to_raw(v) for v in observed_frozenset))
    return to_raw(observed)


def record_new_reactive_obj(original: T, observed: T) -> T:
    __global_reactive_object_map[id(original)] = observed
    __global_original_object_map[id(observed)] = original
    if DEBUG:
        print(
            f'record_new_reactive_obj: {original} at {hex(id(original))} ({id(original)}) -> {observed} at {hex(id(observed))} ({id(observed)})'
        )
    return observed


def mark_raw(instance: T) -> T:
    if DEBUG:
        print(f'mark_raw: {instance} at {hex(id(instance))} ({id(instance)})')
    __marked_raw_set.add(id(instance))
    return instance


def is_marked_raw(instance: object) -> bool:
    return id(instance) in __marked_raw_set
