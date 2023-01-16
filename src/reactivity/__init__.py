# pyright: reportMissingTypeStubs=false

from reactivity.computed import ComputedRef, computed, is_computed_ref
from reactivity.effect import ReactiveEffect, effect
from reactivity.patches import patch
from reactivity.reactive import is_reactive, mark_raw, reactive, to_raw
from reactivity.ref import Ref, is_ref, ref, unref
from reactivity.watch import watch, watch_effect

from .__version__ import __version__

watchEffect = watch_effect
toRaw = to_raw
isReactive = is_reactive
isRef = is_ref
markRaw = mark_raw
isComputedRef = is_computed_ref

patch()

__all__ = [
    'effect', 'watch_effect', 'watchEffect', 'watch', 'reactive', 'ref', 'computed', 'is_reactive', 'is_ref', 'unref',
    '__version__', 'to_raw', 'toRaw', 'isReactive', 'isRef', 'mark_raw', 'markRaw', 'is_computed_ref', 'isComputedRef',
    'Ref', 'ComputedRef', 'ReactiveEffect'
]
