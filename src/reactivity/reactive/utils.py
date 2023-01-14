from typing import Dict, Set, TypeVar, Union, cast

from reactivity.effect.definations import ReactiveEffectDef
from reactivity.effect.utils import (active_effect_stack, track_effects, trigger_effects)
from reactivity.env import DEV
from reactivity.flags import FLAG_OF_REACTIVE

T = TypeVar('T')

reactive_class_map: Dict[type, type] = {}
reactive_reversed_class_map: Dict[type, type] = {}
reactive_deps_map: 'Dict[int, Dict[Union[str, int], Set[ReactiveEffectDef]]]' = {}

__global_reactive_object_map: Dict[int, object] = {}
__global_original_object_map: Dict[int, object] = {}

__marked_raw_set: Set[int] = set()


def is_reactive(obj: object) -> bool:
    return hasattr(obj, FLAG_OF_REACTIVE)


def is_reactive_multable_sequence(obj: object) -> bool:
    return hasattr(obj, '__setitem__') and hasattr(obj, '__getitem__') and is_reactive(obj)


def __get_reactive_subscribers(obj: object, key: Union[str, int]) -> Set[ReactiveEffectDef]:
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


def trigger_reactive(obj: object, key: str) -> None:
    subscribers = __get_reactive_subscribers(obj, key)
    trigger_effects(subscribers)


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


def record_new_reactive_obj(original: T, observed: T) -> T:
    __global_reactive_object_map[id(original)] = observed
    __global_original_object_map[id(observed)] = original
    if DEV:
        print(
            f'record_new_reactive_obj: {original} at {hex(id(original))} ({id(original)}) -> {observed} at {hex(id(observed))} ({id(observed)})'
        )
    return observed


def mark_raw(instance: T) -> T:
    if DEV:
        print(f'mark_raw: {instance} at {hex(id(instance))} ({id(instance)})')
    __marked_raw_set.add(id(instance))
    return instance


def is_marked_raw(instance: object) -> bool:
    return id(instance) in __marked_raw_set
