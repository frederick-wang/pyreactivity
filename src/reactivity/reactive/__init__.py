# reactivity/reactive.py

import types
from typing import Sequence, Set, TypeVar

from reactivity.env import DEV
from reactivity.flags import FLAG_OF_REACTIVE, FLAG_OF_SKIP, REACTIVITY_VALUE
from reactivity.ref.utils import is_ref

from .vars import immutable_builtin_types, supported_builtin_types
from .utils import (get_global_reactive_obj, is_in_global_original_object_map, is_in_global_reactive_object_map,
                    is_marked_raw, is_reactive, mark_raw, reactive_class_map, reactive_reversed_class_map,
                    record_new_reactive_obj, to_raw, track_reactive, trigger_reactive)

T = TypeVar('T')


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

    def __new__(cls, name, bases, attrs):
        # Check if None is in bases, if so, it means that this is the first call to __new__ and we should not do anything
        if None in bases:
            return None
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
    def wrap_attr_methods(proxy_cls, patched_track_methods: Set[str], patched_trigger_methods: Set[str]):
        # sourcery skip: assign-if-exp, reintroduce-else

        has_setattr = hasattr(proxy_cls, '__setattr__')
        if has_setattr:
            raw__setattr__ = getattr(proxy_cls, '__setattr__')

        if hasattr(proxy_cls, '__getattribute__'):
            raw__getattribute__ = getattr(proxy_cls, '__getattribute__')

            def __getattribute__(self, name):
                # If the attribute is patched, return the original attribute and do not track it
                is_magic: bool = name.startswith('__') and name.endswith('__')
                if name in patched_track_methods or name in patched_trigger_methods or is_magic:
                    return raw__getattribute__(self, name)
                    # return original.__getattribute__(name)
                if is_in_global_original_object_map(self):
                    original = to_raw(self)
                    track_reactive(self, name)
                    if DEV:
                        print(f'''[Reactive] track({name}): self={repr(self)} at {hex(id(self))} ({id(self)})''')

                    # result = raw__getattribute__(self, name)
                    result = original.__getattribute__(name)
                    if callable(result):
                        result = raw__getattribute__(self, name)
                    else:
                        raw__getattribute__(self, name)  # A hack to trigger the __getattribute__ of the reactive object
                else:
                    # 如果是一个自定义类，那在初始化响应式对象时，可能会执行一些操作，
                    # 但此时还没有将响应式对象和原始对象关联在一起，只对响应式对象操作即可
                    track_reactive(self, name)
                    if DEV:
                        print(f'''[Reactive] track({name}): self={repr(self)} at {hex(id(self))} ({id(self)})''')
                    result = raw__getattribute__(self, name)

                if is_ref(result):
                    return result.value
                return reactive(result)

            setattr(proxy_cls, '__getattribute__', __getattribute__)
            patched_track_methods.add('__getattribute__')

        if has_setattr:

            def __setattr__(self, name, value):
                if is_reactive(value):
                    value = to_raw(value)
                if is_in_global_original_object_map(self):
                    original = to_raw(self)
                    old_value = original.__getattribute__(name) if hasattr(self, name) else None
                    if old_value == value:
                        return
                    original.__setattr__(name, value)
                else:
                    # 如果是一个自定义类，那在初始化响应式对象时，可能会执行一些操作，
                    # 但此时还没有将响应式对象和原始对象关联在一起，只对响应式对象操作即可
                    old_value = raw__getattribute__(self, name) if hasattr(self, name) else None
                    if old_value == value:
                        return
                    raw__setattr__(self, name, value)
                trigger_reactive(self, name)
                if DEV:
                    print(
                        f'''[Reactive] __setattr__: name={name}, value={value}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                    )

            setattr(proxy_cls, '__setattr__', __setattr__)
            patched_trigger_methods.add('__setattr__')

        if hasattr(proxy_cls, '__delattr__'):
            raw__delattr__ = getattr(proxy_cls, '__delattr__')

            def __delattr__(self, name):
                if is_in_global_original_object_map(self):
                    original = to_raw(self)
                    original.__delattr__(name)
                else:
                    raw__delattr__(self, name)
                trigger_reactive(self, name)
                if DEV:
                    print(f'''[Reactive] __delattr__: name={name}, self={repr(self)} at {hex(id(self))} ({id(self)})''')

            setattr(proxy_cls, '__delattr__', __delattr__)
            patched_trigger_methods.add('__delattr__')

        if hasattr(proxy_cls, '__dir__'):
            raw__dir__ = getattr(proxy_cls, '__dir__')

            def __dir__(self):
                track_reactive(self, '__dir__')
                if DEV:
                    print(f'''[Reactive] __dir__: self={repr(self)} at {hex(id(self))} ({id(self)})''')

                if is_in_global_original_object_map(self):
                    original = to_raw(self)
                    return original.__dir__()
                else:
                    return raw__dir__(self)

            setattr(proxy_cls, '__dir__', __dir__)
            patched_track_methods.add('__dir__')

    @staticmethod
    def wrap_dict_get_method(proxy_cls, patched_track_methods: Set[str]):
        has_setitem = hasattr(proxy_cls, '__setitem__')

        if has_setitem:
            raw__setitem__ = getattr(proxy_cls, '__setitem__')

        if hasattr(proxy_cls, 'get'):
            raw_get = getattr(proxy_cls, 'get')

            def get(self, key, default=None):
                original = to_raw(self)
                track_reactive(self, REACTIVITY_VALUE)
                if DEV:
                    print(
                        f'''[Reactive] track(get): key={key}, default={default}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                    )
                result = original.get(key, default)
                return result.value if is_ref(result) else reactive(result)

            setattr(proxy_cls, 'get', get)
            patched_track_methods.add('get')

    @staticmethod
    def wrap_item_methods(proxy_cls, patched_methods: Set[str], patched_trigger_methods: Set[str]):
        # sourcery skip: assign-if-exp, reintroduce-else
        has_getitem = hasattr(proxy_cls, '__getitem__')
        has_setitem = hasattr(proxy_cls, '__setitem__')

        if has_setitem:
            raw__setitem__ = getattr(proxy_cls, '__setitem__')

        if has_getitem:
            raw__getitem__ = getattr(proxy_cls, '__getitem__')

            def __getitem__(self, key):
                original = to_raw(self)
                track_reactive(self, REACTIVITY_VALUE)
                if DEV:
                    print(
                        f'''[Reactive] track(__getitem__): key={key}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                    )
                result = original.__getitem__(key)
                if is_ref(result) and not isinstance(self, list):
                    return result.value
                return reactive(result)

            setattr(proxy_cls, '__getitem__', __getitem__)
            patched_methods.add('__getitem__')

        if has_setitem:

            def __setitem__(self, key, value):
                if is_reactive(value):
                    value = to_raw(value)
                original = to_raw(self)
                # old_value = raw__getitem__(self, key) if key in self else None
                old_value = original.__getitem__(key) if key in self else None
                if old_value == value:
                    return
                # raw__setitem__(self, key, value)
                original.__setitem__(key, value)
                trigger_reactive(self, REACTIVITY_VALUE)
                if DEV:
                    print(
                        f'''[Reactive] trigger(__setitem__): key={key}, value={value}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                    )

            setattr(proxy_cls, '__setitem__', __setitem__)
            patched_trigger_methods.add('__setitem__')

    @staticmethod
    def wrap_track_method(proxy_cls, method_name: str, patched_methods: Set[str]) -> None:
        if not hasattr(proxy_cls, method_name) or method_name in patched_methods:
            return

        raw_method = getattr(proxy_cls, method_name)

        def wrapper(self, *args, **kwargs):
            original = to_raw(self)
            track_reactive(self, REACTIVITY_VALUE)
            if DEV:
                print(
                    f'''[Reactive] track({method_name}): args={args}, kwargs={kwargs}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                )
            # result = raw_method(self, *args, **kwargs)
            result = original.__getattribute__(method_name)(*args, **kwargs)
            return result

        setattr(proxy_cls, method_name, wrapper)
        patched_methods.add(method_name)

    @staticmethod
    def wrap_trigger_method(proxy_cls, method_name: str, patched_methods: Set[str]) -> None:
        if not hasattr(proxy_cls, method_name) or method_name in patched_methods:
            return

        raw_method = getattr(proxy_cls, method_name)

        def wrapper(self, *args, **kwargs):
            original = to_raw(self)
            # result = raw_method(self, *args, **kwargs)
            result = original.__getattribute__(method_name)(*args, **kwargs)
            trigger_reactive(self, REACTIVITY_VALUE)
            if DEV:
                print(
                    f'''[Reactive] trigger({method_name}): args={args}, kwargs={kwargs}, self={repr(self)} at {hex(id(self))} ({id(self)})'''
                )
            return result

        setattr(proxy_cls, method_name, wrapper)
        patched_methods.add(method_name)


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

    if isinstance(instance, supported_builtin_types):
        # For built-in types, we need to create a new class inherited from the original class to make it reactive
        # We specifically optimize the built-in types that are commonly used in the project
        # These built-in types are: list, bytearray, memoryview, set, dict
        return __create_proxy(instance)

    # For user defined types, we can directly make it reactive
    return __create_proxy(instance, init_with_instance=False)


def get_patched_class(instance):
    raw_class = instance.__class__
    if raw_class not in reactive_class_map:
        class_name = raw_class.__name__
        reactive_class_map[raw_class] = types.new_class(class_name, (raw_class,), {'metaclass': ProxyMetaClass})
        reactive_reversed_class_map[reactive_class_map[raw_class]] = raw_class
    return reactive_class_map[raw_class]


def __create_proxy(instance, init_with_instance=True):
    if DEV:
        print(f'[Reactive] create proxy: {instance}')
    patched_class = get_patched_class(instance)
    if init_with_instance:
        return record_new_reactive_obj(instance, patched_class(instance))  # 如果这里不填上 instance 初始化，json.dumps 输出内容会为空
    return record_new_reactive_obj(instance, patched_class())


__all__ = ['reactive', 'to_raw', 'mark_raw']
