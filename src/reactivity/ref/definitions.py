from typing import Generic, TypeVar

T = TypeVar('T')


class Ref(Generic[T]):
    '''Type differentiator only. Do not use directly.'''
    value: T
