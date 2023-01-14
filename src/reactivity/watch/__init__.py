from inspect import signature, isfunction
from typing import Any, Callable, List, Sequence, TypeVar, Union, cast, overload

from reactivity.reactive.utils import is_reactive
from reactivity.reactive.vars import immutable_builtin_types
from reactivity.ref.definitions import Ref
from reactivity.ref.utils import is_ref

from reactivity.effect import effect

T = TypeVar('T')

StopHandle = Callable[[], None]

WatchSource = Union[Ref[T], Callable[[], T], T]

OnCleanup = Callable[[Callable[[], None]], None]

WatchCallback = Union[Callable[[T, T, OnCleanup], Any], Callable[[T, T], Any], Callable[[T], Any], Callable[[], Any]]


def __get_fn_params_count(fn: Callable) -> int:
    return len(signature(fn).parameters)


@overload
def watch_effect(update: Callable[[], Any]) -> StopHandle:
    ...


@overload
def watch_effect(update: Callable[[OnCleanup], Any]) -> StopHandle:
    ...


def watch_effect(update: Union[Callable[[], Any], Callable[[OnCleanup], None]], **kwargs) -> StopHandle:
    default_kwargs = {}
    for k in kwargs:
        if k not in default_kwargs:
            raise TypeError(f'TypeError: Unknown keyword argument {k} for watch_effect().')
        if type(kwargs[k]) != type(default_kwargs[k]):
            raise TypeError(
                f'TypeError: The type of {k} must be {type(default_kwargs[k])} for watch_effect(), but got {type(kwargs[k])}.')

    stop_flag = False

    update_fn_params_count = __get_fn_params_count(update)

    cleanup_callback: Union[Callable[[], None], None] = None

    def stop():
        nonlocal stop_flag, cleanup_callback

        stop_flag = True

        if cleanup_callback is not None:
            cleanup_callback()
            cleanup_callback = None

    def watch_effect_wrapper():
        nonlocal stop_flag

        if stop_flag:
            return

        if cleanup_callback is not None:
            cleanup_callback()

        def cleanup(cb: Callable[[], None]):
            nonlocal cleanup_callback
            cleanup_callback = cb

        if update_fn_params_count == 0:
            update_fn = cast(Callable[[], None], update)
            update_fn()
        else:
            update_fn = cast(Callable[[OnCleanup], None], update)
            update_fn(cleanup)

    effect(watch_effect_wrapper)

    return stop


def __deeply_walk(obj: object) -> None:
    if is_ref(obj):
        obj = cast(Ref, obj).value
    if not is_reactive(obj):
        return
    if isinstance(obj, dict):
        for k in obj:
            __deeply_walk(obj[k])
    elif isinstance(obj, (list, set)):
        for v in obj:
            __deeply_walk(v)


@overload
def watch(
    source: WatchSource[T],
    callback: WatchCallback[T],
    *,
    deep: bool = False,
    immediate: bool = False,
    **kwargs,
) -> StopHandle:
    ...


@overload
def watch(
    source: Sequence[WatchSource[T]],
    callback: WatchCallback[List[T]],
    *,
    deep: bool = False,
    immediate: bool = False,
    **kwargs,
) -> StopHandle:
    ...


def watch(
    source: Union[WatchSource[T], Sequence[WatchSource[T]]],
    callback: Union[WatchCallback[T], WatchCallback[List[T]]],
    *,
    deep: bool = False,
    immediate: bool = False,
    **kwargs,
) -> StopHandle:
    '''
    Watch a source and run a callback when the source changes.
    
    Args:
        source: The source to watch.
        callback: The callback to run when the source changes.

    Keyword Args:
        deep: Whether to watch the source deeply. Defaults to False.
        immediate: Whether to run the callback immediately. Defaults to False.
    
    Returns:
        A function to stop watching.
    '''
    default_kwargs = {
        'immediate': False,
        'deep': False,
    }
    kwargs.update({
        'immediate': immediate,
        'deep': deep,
    })
    for k in kwargs:
        if k not in default_kwargs:
            raise TypeError(f'TypeError: Unknown keyword argument {k} for watch().')
        if type(kwargs[k]) != type(default_kwargs[k]):
            raise TypeError(
                f'TypeError: The type of {k} must be {type(default_kwargs[k])} for watch(), but got {type(kwargs[k])}.')
    immediate = kwargs.get('immediate', default_kwargs['immediate'])
    deep = kwargs.get('deep', default_kwargs['deep'])

    stop_flag = False

    cleanup_callback: Union[Callable[[], None], None] = None

    def stop():
        nonlocal stop_flag, cleanup_callback

        stop_flag = True

        if cleanup_callback is not None:
            cleanup_callback()
            cleanup_callback = None

    if isinstance(source, Sequence) and not is_reactive(source):
        src_list = cast(List[WatchSource[T]], list(source))
        SINGLE_SRC_MOD = False
    else:
        src_list = cast(List[WatchSource[T]], [source])
        SINGLE_SRC_MOD = True
    for src in src_list:
        if not is_reactive(src) and not is_ref(src) and not isfunction(src):
            raise TypeError(f'TypeError: Invalid watch source type: {type(src)} for watch().')

    N = len(src_list)
    old_value_list: List[Union[T, None]] = [None] * N
    is_first_run = True

    def gen_fn(i: int) -> Callable[[], T]:
        src = src_list[i]
        need_walk_deep = deep
        if is_reactive(src):
            need_walk_deep = True

        def fn() -> T:
            if isfunction(src):
                res = src()
            elif is_ref(src):
                res = cast(Ref[T], src).value
            elif is_reactive(src):
                res = src
            else:
                raise TypeError(f'TypeError: Invalid watch source type: {type(src)} for watch().')
            res = cast(T, res)
            if need_walk_deep:
                __deeply_walk(res)
            return res

        return fn

    fn_list = [gen_fn(i) for i in range(N)]
    params_cnt = __get_fn_params_count(callback)

    def calc_new_value_list() -> List[T]:
        unfilled_new_value_list: List[Union[T, None]] = [None] * N
        for i in range(N):
            fn = fn_list[i]
            new_value = fn()
            unfilled_new_value_list[i] = new_value
        new_value_list = cast(List[T], unfilled_new_value_list)
        return new_value_list

    def watch_wrapper():
        nonlocal stop_flag, is_first_run

        if stop_flag:
            return

        if cleanup_callback is not None:
            cleanup_callback()

        def cleanup(cb: Callable[[], None]):
            nonlocal cleanup_callback
            cleanup_callback = cb

        try:
            new_value_list = calc_new_value_list()

            skip = True
            # Check if the value has changed, if not, skip the callback.
            for i in range(N):
                new_value = new_value_list[i]
                old_value = old_value_list[i]
                if new_value != old_value:
                    skip = False
                    break
                # If the new_value and the old_value are the same object, we cannot judge if the value has changed.
                # So we still need to run the callback.
                if not isinstance(new_value, immutable_builtin_types) and new_value is old_value:
                    skip = False
                    break
            # Check if it's the first run and `immediate` is False, if so, skip the callback.
            if is_first_run and not immediate:
                old_value_list[:] = new_value_list
                skip = True
            if skip:
                return

            if params_cnt == 0:
                cb = cast(Callable[[], None], callback)
                cb()
            elif params_cnt == 1:
                if SINGLE_SRC_MOD:
                    cb = cast(Callable[[T], None], callback)
                    cb(new_value_list[0])
                else:
                    cb = cast(Callable[[List[T]], None], callback)
                    cb(new_value_list)
            elif params_cnt == 2:
                if SINGLE_SRC_MOD:
                    cb = cast(Callable[[T, Union[T, None]], None], callback)
                    cb(new_value_list[0], old_value_list[0])
                else:
                    cb = cast(Callable[[List[T], List[Union[T, None]]], None], callback)
                    cb(new_value_list, old_value_list[:])
            elif params_cnt == 3:
                if SINGLE_SRC_MOD:
                    cb = cast(Callable[[T, Union[T, None], OnCleanup], None], callback)
                    cb(new_value_list[0], old_value_list[0], cleanup)
                else:
                    cb = cast(Callable[[List[T], List[Union[T, None]], OnCleanup], None], callback)
                    cb(new_value_list, old_value_list[:], cleanup)
            else:
                raise TypeError(
                    f'TypeError: Invalid callback function for watch(). The callback function must have 0, 1 or 2 parameters, but got {params_cnt} parameters.'
                )

            old_value_list[:] = new_value_list
        finally:
            if is_first_run:
                is_first_run = False

    effect(watch_wrapper)

    return stop
