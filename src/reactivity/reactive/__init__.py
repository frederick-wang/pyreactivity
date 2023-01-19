# pyright: reportMissingTypeStubs=false

import types
from typing import (Any, Dict, ItemsView, Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple,
                    TypeVar, Union, ValuesView, cast, overload)

from reactivity.env import DEBUG
from reactivity.flags import FLAG_OF_REACTIVE, FLAG_OF_SKIP
from reactivity.ref.definitions import Ref
from reactivity.ref.utils import is_ref

from .utils import (deep_to_raw, get_global_reactive_obj, is_in_global_reactive_object_map, is_marked_raw, is_reactive,
                    mark_raw, reactive_class_map, reactive_reversed_class_map, record_new_reactive_obj, to_raw,
                    track_reactive, track_reactive_value, trigger_reactive, trigger_reactive_value)
from .vars import immutable_builtin_types

T = TypeVar('T')
U = TypeVar('U')


@overload
def _unref_and_reactive(obj: Ref[T]) -> T:
    ...


@overload
def _unref_and_reactive(obj: T) -> T:
    ...


def _unref_and_reactive(obj: Union[Ref[T], T]) -> T:
    return cast(Ref[T], obj).value if is_ref(obj) else reactive(cast(T, obj))


class dict_items(ItemsView[T, U]):
    _mapping: Mapping[T, U]

    def __contains__(self, item: object) -> bool:
        item = cast(Tuple[T, U], item)
        key, value = item
        try:
            v = _unref_and_reactive(self._mapping[key])
        except KeyError:
            return False
        else:
            return v is value or v == value

    def __iter__(self):
        for key in self._mapping:
            yield (key, _unref_and_reactive(self._mapping[key]))


class dict_values(ValuesView[U]):
    _mapping: Mapping[Any, U]

    def __contains__(self, value: object) -> bool:
        for key in self._mapping:
            v = _unref_and_reactive(self._mapping[key])
            if v is value or v == value:
                return True
        return False

    def __iter__(self):
        for key in self._mapping:
            yield _unref_and_reactive(self._mapping[key])


class ProxyMetaClass(type):
    general_track_methods: Set[str] = {
        # basic
        '__str__',
        '__bytes__',
        '__format__',
        '__lt__',
        '__le__',
        '__eq__',
        '__ne__',
        '__gt__',
        '__ge__',
        '__hash__',
        '__bool__',
        # callable objects
        '__call__',
        # emulating container types
        '__len__',
        '__length_hint__',
        '__missing__',
        '__iter__',
        '__reversed__',
        '__contains__',
        # emulating numeric types
        '__add__',
        '__sub__',
        '__mul__',
        '__matmul__',
        '__truediv__',
        '__floordiv__',
        '__mod__',
        '__divmod__',
        '__pow__',
        '__lshift__',
        '__rshift__',
        '__and__',
        '__xor__',
        '__or__',
        '__radd__',
        '__rsub__',
        '__rmul__',
        '__rmatmul__',
        '__rtruediv__',
        '__rfloordiv__',
        '__rmod__',
        '__rdivmod__',
        '__rpow__',
        '__rlshift__',
        '__rrshift__',
        '__rand__',
        '__rxor__',
        '__ror__',
        '__neg__',
        '__pos__',
        '__abs__',
        '__invert__',
        '__complex__',
        '__int__',
        '__float__',
        '__index__',
        '__round__',
        '__trunc__',
        '__floor__',
        '__ceil__',
        # with statement context managers
        '__enter__',
        '__exit__',
        # customing positional arguments in class pattern matching
        '__match_args__',
        # awaitable objects
        '__await__',
        # asynchronous iterators
        '__aiter__',
        '__anext__',
        # asynchronous context managers
        '__aenter__',
        '__aexit__'
    }
    general_trigger_methods: Set[str] = {
        # emulating container types
        '__delitem__',
        # emulating numeric types
        '__iadd__',
        '__isub__',
        '__imul__',
        '__imatmul__',
        '__itruediv__',
        '__ifloordiv__',
        '__imod__',
        '__ipow__',
        '__ilshift__',
        '__irshift__',
        '__iand__',
        '__ixor__',
        '__ior__'
    }
    sequence_track_methods: Set[str] = {'index', 'count', 'copy'}
    sequence_trigger_methods: Set[str] = {'append', 'clear', 'extend', 'insert', 'pop', 'remove', 'reverse'}
    list_track_methods: Set[str] = set()
    list_trigger_methods: Set[str] = {'sort'}
    bytearray_track_methods: Set[str] = {
        # bytes and bytearray common methods
        'count',
        'removeprefix',
        'removesuffix',
        'decode',
        'endswith',
        'find',
        'index',
        'join',
        'maketrans',
        'partition',
        'replace',
        'rfind',
        'rindex',
        'rpartition',
        'startswith',
        'translate',
        'center',
        'ljust',
        'lstip',
        'rjust',
        'rsplit',
        'rstrip',
        'split',
        'strip',
        'capitalize',
        'expandtabs',
        'isalnum',
        'isalpha',
        'isasii',
        'isdigit',
        'islower',
        'isspace',
        'istitle',
        'isupper',
        'lower',
        'splitlines',
        'swapcase',
        'title',
        'upper',
        'zfill',
        # bytearray-specific methods
        'fromhex',
        'hex'
    }
    bytearray_trigger_methods: Set[str] = set()
    memoryview_track_methods: Set[str] = {
        'tobytes', 'hex', 'tolist', 'toreadonly', 'cast', 'obj', 'nbytes', 'readonly', 'format', 'itemsize', 'ndim',
        'shape', 'strides', 'suboffsets', 'c_contiguous', 'f_contiguous', 'contiguous'
    }
    memoryview_trigger_methods: Set[str] = {'release'}
    set_track_methods: Set[str] = {
        # set and frozenset common methods
        'isdisjoint',
        'issubset',
        'issuperset',
        'union',
        'intersection',
        'difference',
        'symmetric_difference',
        'copy'
    }
    set_trigger_methods: Set[str] = {
        'update', 'intersection_update', 'difference_update', 'symmetric_difference_update', 'add', 'remove', 'discard',
        'pop', 'clear'
    }
    dict_track_methods: Set[str] = {'copy', 'fromkeys', 'get', 'items', 'keys', 'reversed', 'values'}
    dict_trigger_methods: Set[str] = {'clear', 'pop', 'popitem', 'setdefault', 'update'}

    def __new__(cls, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any]) -> Optional[type]:
        # Check if None is in bases, if so, it means that this is the first call to __new__ and we should not do anything
        if type(None) in bases:
            return None

        # Clear the __init__ method of the proxy class
        def __init__(self: object, *args: Any, **kwargs: Any):
            pass

        attrs['__init__'] = __init__
        proxy_cls = type.__new__(cls, name, bases, attrs)

        patched_track_methods: Set[str] = set()
        patched_trigger_methods: Set[str] = set()

        # patch list methods
        if issubclass(proxy_cls, list):
            for list_track_method in cls.list_track_methods:
                cls.wrap_track_method(proxy_cls, list_track_method, patched_track_methods)
            for list_trigger_method in cls.list_trigger_methods:
                cls.wrap_trigger_method(proxy_cls, list_trigger_method, patched_trigger_methods)
        # patch bytearray methods
        if issubclass(proxy_cls, bytearray):
            for bytearray_track_method in cls.bytearray_track_methods:
                cls.wrap_track_method(proxy_cls, bytearray_track_method, patched_track_methods)
            for bytearray_trigger_method in cls.bytearray_trigger_methods:
                cls.wrap_trigger_method(proxy_cls, bytearray_trigger_method, patched_trigger_methods)
        # patch sequence methods
        if issubclass(proxy_cls, Sequence):
            for sequence_track_method in cls.sequence_track_methods:
                cls.wrap_track_method(proxy_cls, sequence_track_method, patched_track_methods)
            for sequence_trigger_method in cls.sequence_trigger_methods:
                cls.wrap_trigger_method(proxy_cls, sequence_trigger_method, patched_trigger_methods)
        # patch memoryview methods
        if issubclass(proxy_cls, memoryview):
            for memoryview_track_method in cls.memoryview_track_methods:
                cls.wrap_track_method(proxy_cls, memoryview_track_method, patched_track_methods)
            for memoryview_trigger_method in cls.memoryview_trigger_methods:
                cls.wrap_trigger_method(proxy_cls, memoryview_trigger_method, patched_trigger_methods)
        # patch set methods
        if issubclass(proxy_cls, set):
            for set_track_method in cls.set_track_methods:
                cls.wrap_track_method(proxy_cls, set_track_method, patched_track_methods)
            for set_trigger_method in cls.set_trigger_methods:
                cls.wrap_trigger_method(proxy_cls, set_trigger_method, patched_trigger_methods)
        # patch dict methods
        if issubclass(proxy_cls, dict):
            cls.wrap_dict_view_method(proxy_cls, patched_track_methods)
            cls.wrap_dict_get_method(proxy_cls, patched_track_methods)
            for dict_track_method in cls.dict_track_methods:
                cls.wrap_track_method(proxy_cls, dict_track_method, patched_track_methods)
            for dict_trigger_method in cls.dict_trigger_methods:
                cls.wrap_trigger_method(proxy_cls, dict_trigger_method, patched_trigger_methods)
        # patch general methods
        for general_track_method in cls.general_track_methods:
            cls.wrap_track_method(proxy_cls, general_track_method, patched_track_methods)
        for general_trigger_method in cls.general_trigger_methods:
            cls.wrap_trigger_method(proxy_cls, general_trigger_method, patched_trigger_methods)

        cls.wrap_item_methods(proxy_cls, patched_track_methods, patched_trigger_methods)
        cls.wrap_attr_methods(proxy_cls, patched_track_methods, patched_trigger_methods)

        # Set the sign of reactive object
        setattr(proxy_cls, FLAG_OF_REACTIVE, True)

        return proxy_cls

    @staticmethod
    def wrap_attr_methods(proxy_cls: type, patched_track_methods: Set[str], patched_trigger_methods: Set[str]):
        # sourcery skip: assign-if-exp, reintroduce-else

        has_setattr = hasattr(proxy_cls, '__setattr__')

        if hasattr(proxy_cls, '__getattribute__'):
            raw__getattribute__ = getattr(proxy_cls, '__getattribute__')

            def __getattribute__(self: object, name: str):
                # If the attribute is patched, return the original attribute and do not track it
                is_magic: bool = name.startswith('__') and name.endswith('__')
                if name in patched_track_methods or name in patched_trigger_methods or is_magic:
                    return raw__getattribute__(self, name)

                original = to_raw(self)
                track_reactive(self, name)
                if DEBUG:
                    print(f'''[Reactive] track({name}): self={repr(self)} at {hex(id(self))} ({id(self)})''')

                result = original.__getattribute__(name)
                if name in original.__class__.__dict__ and getattr(original.__class__, name) and isinstance(
                        getattr(original.__class__, name), property):
                    result = raw__getattribute__(self, name)
                if callable(result):
                    result = raw__getattribute__(self, name)

                if is_ref(result):
                    return result.value
                return reactive(result)

            setattr(proxy_cls, '__getattribute__', __getattribute__)
            patched_track_methods.add('__getattribute__')

        if has_setattr:

            def __setattr__(self: object, name: str, value: Any):
                if is_reactive(value):
                    value = to_raw(value)
                original = to_raw(self)
                old_value = original.__getattribute__(name) if hasattr(self, name) else None
                if is_ref(old_value):
                    old_value = cast(Ref[Any], old_value)
                    if is_ref(value):
                        value = cast(Ref[Any], value)
                        if old_value.value == value.value:
                            return
                        original.__setattr__(name, value)
                    else:
                        if old_value.value == value:
                            return
                        old_value.value = value
                else:
                    if old_value == value:
                        return
                    original.__setattr__(name, value)
                trigger_reactive(self, name)
                if DEBUG:
                    print(
                        f'''[Reactive] __setattr__: name={name}, value={value}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                    )

            setattr(proxy_cls, '__setattr__', __setattr__)
            patched_trigger_methods.add('__setattr__')

        if hasattr(proxy_cls, '__delattr__'):

            def __delattr__(self: object, name: str):
                original = to_raw(self)
                original.__delattr__(name)
                trigger_reactive(self, name)
                if DEBUG:
                    print(f'''[Reactive] __delattr__: name={name}, self={repr(self)} at {hex(id(self))} ({id(self)})''')

            setattr(proxy_cls, '__delattr__', __delattr__)
            patched_trigger_methods.add('__delattr__')

        if hasattr(proxy_cls, '__dir__'):

            def __dir__(self: object):
                track_reactive(self, '__dir__')
                if DEBUG:
                    print(f'''[Reactive] __dir__: self={repr(self)} at {hex(id(self))} ({id(self)})''')
                original = to_raw(self)
                return original.__dir__()

            setattr(proxy_cls, '__dir__', __dir__)
            patched_track_methods.add('__dir__')

    @staticmethod
    def wrap_item_methods(proxy_cls: type, patched_methods: Set[str], patched_trigger_methods: Set[str]):
        # sourcery skip: assign-if-exp, reintroduce-else
        has_getitem = hasattr(proxy_cls, '__getitem__')
        has_setitem = hasattr(proxy_cls, '__setitem__')

        if has_getitem:

            def __getitem__(self: Union[Sequence[Any], Mapping[Any, Any]], key: slice):
                original = to_raw(self)
                track_reactive_value(self)
                if DEBUG:
                    print(
                        f'''[Reactive] track(__getitem__): key={key}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                    )
                result = original.__getitem__(key)
                if is_ref(result) and not isinstance(self, list):
                    return cast(Ref[Any], result).value
                return reactive(result)

            setattr(proxy_cls, '__getitem__', __getitem__)
            patched_methods.add('__getitem__')

        if has_setitem:

            def __setitem__(self: Union[MutableSequence[Any], MutableMapping[Any, Any]], key: slice, value: Any):
                if is_reactive(value):
                    value = to_raw(value)
                original = to_raw(self)
                old_value = original.__getitem__(key) if key in self else None
                if is_ref(old_value):
                    old_value = cast(Ref[Any], old_value)
                    if is_ref(value):
                        value = cast(Ref[Any], value)
                        if old_value.value == value.value:
                            return
                        original.__setitem__(key, value)
                    else:
                        if old_value.value == value:
                            return
                        old_value.value = value
                else:
                    if old_value == value:
                        return
                    original.__setitem__(key, value)
                trigger_reactive_value(self)
                if DEBUG:
                    print(
                        f'''[Reactive] trigger(__setitem__): key={key}, value={value}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                    )

            setattr(proxy_cls, '__setitem__', __setitem__)
            patched_trigger_methods.add('__setitem__')

    @staticmethod
    def wrap_track_method(proxy_cls: type, method_name: str, patched_methods: Set[str]) -> None:
        if not hasattr(proxy_cls, method_name) or method_name in patched_methods:
            return

        def wrapper(self: object, *args: Any, **kwargs: Any):
            original = to_raw(self)
            track_reactive_value(self)
            if DEBUG:
                print(
                    f'''[Reactive] track({method_name}): args={args}, kwargs={kwargs}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                )
            result = original.__getattribute__(method_name)(*args, **kwargs)
            return result

        setattr(proxy_cls, method_name, wrapper)
        patched_methods.add(method_name)

    @staticmethod
    def wrap_trigger_method(proxy_cls: type, method_name: str, patched_methods: Set[str]) -> None:
        if not hasattr(proxy_cls, method_name) or method_name in patched_methods:
            return

        def wrapper(self: object, *args: Any, **kwargs: Any):
            original = to_raw(self)
            result = original.__getattribute__(method_name)(*args, **kwargs)
            trigger_reactive_value(self)
            if DEBUG:
                print(
                    f'''[Reactive] trigger({method_name}): args={args}, kwargs={kwargs}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                )
            return result

        setattr(proxy_cls, method_name, wrapper)
        patched_methods.add(method_name)

    @staticmethod
    def wrap_dict_get_method(proxy_cls: type, patched_track_methods: Set[str]):
        if hasattr(proxy_cls, 'get'):  # Fool-proofing

            def get(self: Dict[Any, Any], key: Any, default: Any = None):
                original = to_raw(self)
                track_reactive_value(self)
                if DEBUG:
                    print(
                        f'''[Reactive] track(get): key={key}, default={default}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                    )
                result = original.get(key, default)
                return result.value if is_ref(result) else reactive(result)

            setattr(proxy_cls, 'get', get)
            patched_track_methods.add('get')

    @staticmethod
    def wrap_dict_view_method(proxy_cls: type, patched_track_methods: Set[str]):
        if hasattr(proxy_cls, 'items'):  # Fool-proofing

            def items(self: Dict[T, U]) -> dict_items[T, U]:
                original: Dict[T, U] = to_raw(self)
                track_reactive_value(self)
                if DEBUG:
                    print(f'''[Reactive] track(items): self={repr(self)} at {hex(id(self))} ({id(self)})''')
                return dict_items(original)

            setattr(proxy_cls, 'items', items)
            patched_track_methods.add('items')

        if hasattr(proxy_cls, 'values'):

            def values(self: Dict[Any, U]) -> dict_values[U]:
                original: Dict[Any, U] = to_raw(self)
                track_reactive_value(self)
                if DEBUG:
                    print(f'''[Reactive] track(values): self={repr(self)} at {hex(id(self))} ({id(self)})''')
                return dict_values(original)

            setattr(proxy_cls, 'values', values)
            patched_track_methods.add('values')


@overload
def reactive(instance: Dict[U, Any]) -> Dict[U, Any]:
    ...


@overload
def reactive(instance: T) -> T:
    ...


def reactive(instance: T) -> T:

    # If the instance is None, return None
    if instance is None:
        return instance

    # If the instance is a callable, return it directly
    if callable(instance):
        return instance

    # If the instance is a ref object, return it directly
    if is_ref(instance):
        return instance

    # If the instance is marked as raw, return it directly
    if is_marked_raw(instance):
        return instance

    # If the instance has skip flag, return it directly
    if hasattr(instance, FLAG_OF_SKIP):
        return instance

    # If the instance is already reactive, return it directly
    if is_reactive(instance):
        return instance

    # If the instance is immutable, return it directly
    if isinstance(instance, immutable_builtin_types):
        # raise TypeError(
        #     f'TypeError: You can only make a mutable object reactive. The type of {instance} is {type(instance)}.')
        return instance

    # If the instance has already been reactive, return the reactive version of it directly
    if is_in_global_reactive_object_map(instance):
        return get_global_reactive_obj(instance)

    return __create_proxy(instance)


def get_patched_class(instance: object):
    raw_class = instance.__class__
    if raw_class not in reactive_class_map:
        class_name = raw_class.__name__
        reactive_class_map[raw_class] = types.new_class(class_name, (raw_class,), {'metaclass': ProxyMetaClass})
        reactive_reversed_class_map[reactive_class_map[raw_class]] = raw_class
    return reactive_class_map[raw_class]


def __create_proxy(instance: object):
    if DEBUG:
        print(f'[Reactive] create proxy: {instance}')
    patched_class = get_patched_class(instance)
    try:
        proxy = patched_class()
        if isinstance(instance, dict):
            # NOTE: According to testing, in the JSONEncoder, when calling c_make_encoder to encode a dict,
            # if something is not initialized here casually, the output of json.dumps will be an empty {}.
            # Example:
            # d = reactive({'a': 1})
            # json.dumps(d)
            cast(Any, dict).__init__(proxy, {None: None})
        elif isinstance(instance, list):
            # NOTE: According to testing, for list, if you don't initialize it with an element, reactive([]) will be equal to any reactive list
            cast(Any, list).__init__(proxy, [None])
        elif isinstance(instance, set):
            # NOTE: According to testing, for set, if you don't initialize it with an element, reactive(set()) will be equal to any reactive set
            cast(Any, set).__init__(proxy, {None})
        elif isinstance(instance, tuple):
            # NOTE: According to testing, for tuple, if you don't initialize it with an element, reactive(()) will be equal to any reactive tuple
            cast(Any, tuple).__init__(proxy, (None,))
    except Exception:
        # If the class supports passing in an instance of itself and directly returning it, then use this feature to bypass the __new__ method。
        # Because we don't know what parameters to fill in for __new__, we can only try to directly pass in an instance of itself.
        proxy = patched_class(instance)
    return record_new_reactive_obj(cast(object, instance), proxy)


__all__ = ['is_reactive', 'mark_raw', 'reactive', 'to_raw', 'deep_to_raw']
