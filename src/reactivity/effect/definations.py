from typing import (Any, Callable, Generic, List, Set, TypeVar, Union)

T = TypeVar('T')


class ReactiveEffectDef(Generic[T]):
    '''Type differentiator only. Do not use directly.'''
    active: bool
    fn: Callable[[], T]
    scheduler: Union[Callable, None]
    computed: Union[Any, None]  # type: ComputedRefImpl[T]
    deps: 'List[Set[ReactiveEffectDef]]'

    def __init__(self, fn: Callable[[], T], scheduler: Union[Callable, None] = None) -> None:
        raise NotImplementedError('ReactiveEffectDef is a type differentiator only. Do not use directly.')

    def run(self) -> T:  # type: ignore
        pass

    def stop(self) -> None:
        pass

    def __call__(self) -> T:  # type: ignore
        pass
