import json
import types
from typing import Any, Dict, Optional, Tuple, cast

from reactivity.ref.definitions import Ref
from reactivity.ref.utils import is_ref

__json_encoder_map: Dict[type, type] = {}


class PyReactivityJSONEncoderMetaClass(type):

    def __new__(cls, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any]) -> Optional[type]:

        proxy_cls = type.__new__(cls, name, bases, attrs)
        raw_default = getattr(proxy_cls, 'default')

        def default(self: object, o: object):
            return cast(Ref[Any], o).value if is_ref(o) else raw_default(self, o)

        setattr(proxy_cls, 'default', default)

        return proxy_cls


def __patch_json_dumps():
    raw_json_dumps = json.dumps

    def dumps(*args: Any, **kwargs: Any):
        raw_class = kwargs['cls'] if 'cls' in kwargs else json.JSONEncoder
        if raw_class not in __json_encoder_map:
            class_name = raw_class.__name__
            __json_encoder_map[raw_class] = types.new_class(
                class_name,
                (raw_class,),
                {'metaclass': PyReactivityJSONEncoderMetaClass},
            )
        kwargs['cls'] = __json_encoder_map[raw_class]
        return raw_json_dumps(*args, **kwargs)

    json.dumps = dumps


def patch():
    __patch_json_dumps()


__all__ = ['patch']
