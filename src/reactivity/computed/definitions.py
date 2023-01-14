from typing import Generic, TypeVar

T = TypeVar('T')


class ComputedRef(Generic[T]):
    '''Type differentiator only. Do not use directly.'''
    value: T
    # effect: ReactiveEffect[T]
