# pyright: reportMissingTypeStubs=false

from reactivity.computed import ComputedRef, computed, is_computed_ref
from reactivity.effect import ReactiveEffect, effect
from reactivity.patches import patch
from reactivity.reactive import (deep_to_raw, is_reactive, mark_raw, reactive, to_raw)
from reactivity.ref import Ref, deep_unref, is_ref, ref, unref
from reactivity.watch import watch, watch_effect

from .__version__ import __version__

watchEffect = watch_effect
toRaw = to_raw
deepToRaw = deep_to_raw
isReactive = is_reactive
markRaw = mark_raw
deepUnref = deep_unref
isRef = is_ref
isComputedRef = is_computed_ref

patch()

__all__ = [
    'effect', 'watch_effect', 'watchEffect', 'watch', 'reactive', 'ref', 'computed', 'is_reactive', 'is_ref', 'unref',
    'deep_unref', 'deepUnref', '__version__', 'to_raw', 'toRaw', 'deep_to_raw', 'deepToRaw', 'isReactive', 'isRef',
    'mark_raw', 'markRaw', 'is_computed_ref', 'isComputedRef', 'Ref', 'ComputedRef', 'ReactiveEffect'
]
