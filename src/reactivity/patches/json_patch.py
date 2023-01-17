import json
import types
from typing import Any, Dict, Optional, Tuple, cast

from reactivity.ref.definitions import Ref
from reactivity.ref.utils import is_ref

__json_encoder_map: Dict[type, type] = {}

__raw_json_dump = json.dump
__raw_json_dumps = json.dumps


class PyReactivityJSONEncoderMetaClass(type):

    def __new__(cls, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any]) -> Optional[type]:

        proxy_cls = type.__new__(cls, name, bases, attrs)
        raw_default = getattr(proxy_cls, 'default')

        def default(self: object, o: object):
            return cast(Ref[Any], o).value if is_ref(o) else raw_default(self, o)

        setattr(proxy_cls, 'default', default)

        return proxy_cls


def __patch_json_dumps():

    def dumps(*args: Any, **kwargs: Any):
        if 'default' in kwargs:
            raw_default = kwargs['default']

            def default(o: object):
                return cast(Ref[Any], o).value if is_ref(o) else raw_default(o)

            kwargs['default'] = default

        raw_class = kwargs['cls'] if 'cls' in kwargs else json.JSONEncoder
        if raw_class not in __json_encoder_map:
            class_name = raw_class.__name__
            __json_encoder_map[raw_class] = types.new_class(
                class_name,
                (raw_class,),
                {'metaclass': PyReactivityJSONEncoderMetaClass},
            )
        kwargs['cls'] = __json_encoder_map[raw_class]

        return __raw_json_dumps(*args, **kwargs)

    json.dumps = dumps


def __patch_json_dump():

    def dump(*args: Any, **kwargs: Any):
        if 'default' in kwargs:
            raw_default = kwargs['default']

            def default(o: object):
                return cast(Ref[Any], o).value if is_ref(o) else raw_default(o)

            kwargs['default'] = default

        raw_class = kwargs['cls'] if 'cls' in kwargs else json.JSONEncoder
        if raw_class not in __json_encoder_map:
            class_name = raw_class.__name__
            __json_encoder_map[raw_class] = types.new_class(
                class_name,
                (raw_class,),
                {'metaclass': PyReactivityJSONEncoderMetaClass},
            )
        kwargs['cls'] = __json_encoder_map[raw_class]

        return __raw_json_dump(*args, **kwargs)

    json.dump = dump


def patch_json():
    __patch_json_dumps()
    __patch_json_dump()


def unpatch_json():
    json.dumps = __raw_json_dumps
    json.dump = __raw_json_dump


def default(o: object):
    if is_ref(o):
        return cast(Ref[Any], o).value
    raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')
