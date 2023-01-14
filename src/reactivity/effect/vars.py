from collections import deque
from typing import Deque
from .definations import ReactiveEffectDef

active_effect_stack: 'Deque[ReactiveEffectDef]' = deque()
