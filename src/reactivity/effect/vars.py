from collections import deque
from typing import Any, Deque
from .definations import ReactiveEffectDef

active_effect_stack: 'Deque[ReactiveEffectDef[Any]]' = deque()
