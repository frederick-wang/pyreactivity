from typing import Set

from .definations import ReactiveEffectDef
from .vars import active_effect_stack


def cleanup_effect(effect: ReactiveEffectDef) -> None:
    if not effect.deps:
        return
    for dep in effect.deps:
        dep.remove(effect)
    effect.deps.clear()


def track_effects(dep: Set[ReactiveEffectDef]):
    active_effect = active_effect_stack[-1]
    dep.add(active_effect)
    if dep not in active_effect.deps:
        active_effect.deps.append(dep)


def trigger_effects(effects: Set[ReactiveEffectDef]):
    effect_list = list(effects)
    for effect in effect_list:
        if effect.computed is not None:
            trigger_effect(effect)
    for effect in effect_list:
        if effect.computed is None:
            trigger_effect(effect)


def trigger_effect(effect: ReactiveEffectDef) -> None:
    if effect.scheduler is None:
        effect.run()
    else:
        effect.scheduler()
