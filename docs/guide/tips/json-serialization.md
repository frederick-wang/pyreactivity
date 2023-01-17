---
prev: ../essentials/watchers
---

# JSON Serialization

**Contents**

[[toc]]

When exchanging data, we often serialize data objects in Python into JSON format strings.

## `json.dumps()` and `json.dump()`

If you are using the built-in `json` module in Python, you do not need to do any additional work, and you can **directly** use `json.dumps` to serialize reactive objects into a JSON string.

```python:no-line-numbers
import json

from reactivity import reactive, ref

obj = reactive({'foo': ref({'bar': [ref(1), 2, 3]})})
print(json.dumps(obj))  # will print: {"foo": {"bar": [1, 2, 3]}}
```

Whether using `reactive()` to generate reactive objects or using `ref()` to generate reactive variables, they can be directly serialized into JSON strings by `json.dumps()`.

If you need to serialize custom objects, you usually define the `default` parameter or the `cls` parameter of `json.dumps`. **Don't worry about setting these two parameters conflicting with PyReactivty, PyReactivity is compatible with them.**

For example, if we need to customize a `default` function that can serialize `complex` type complex objects, after calling `json.dumps`, we can get the correct result:

```python:no-line-numbers
def complex_handler(obj):
    if isinstance(obj, complex):
        return [obj.real, obj.imag]
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

obj = ref({'foo': ref({'bar': [ref(1), 2, 3]}), 'baz': ref(1 + 1j), 'c': 2 + 1j})
print(json.dumps(obj, default=complex_handler))
# will print: {"foo": {"bar": [1, 2, 3]}, "baz": [1.0, 1.0], "c": [2.0, 1.0]}
```

If you prefer to customize the encoder using the `cls` parameter, it is also compatible:

```python:no-line-numbers
class ComplexEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, complex):
            return [obj.real, obj.imag]
        return json.JSONEncoder.default(self, obj)

obj = ref({'foo': ref({'bar': [ref(1), 2, 3]}), 'baz': ref(1 + 1j), 'c': 2 + 1j})
print(json.dumps(obj, cls=ComplexEncoder))
# will print: {"foo": {"bar": [1, 2, 3]}, "baz": [1.0, 1.0], "c": [2.0, 1.0]}
```

## Implementation Principle

When the `reactivity` module is imported for the first time, PyReactivity replaces the `json.dump()` and `json.dumps()` methods, making them able to serialize reactive objects.

If you want to manually control this process, you can import the `patch_json()` and `unpatch_json()` functions from `reactivity.patches`, which are used to replace and restore the `json.dump()` and `json.dumps()` methods, respectively.

If `unpatch_json()` is called, then `json.dumps()` will not be able to serialize reactive objects:

```python:no-line-numbers
from reactivity import ref

from reactivity.patches import patch_json, unpatch_json

a = ref(1)

unpatch_json()
print(json.dumps(a))  # Will raise an error: TypeError: Object is not JSON serializable
```

If `patch_json()` is called after `unpatch_json()`, then `json.dumps()` will regain the ability to serialize reactive objects:

```python:no-line-numbers
from reactivity import ref

from reactivity.patches import patch_json, unpatch_json

a = ref(1)

unpatch_json()
patch_json()
print(json.dumps(a))  # will print: 1
```

## Third-Party JSON Libraries

If you are using a third-party JSON library such as `simplejson`, they default to only supporting the serialization of reactive objects generated by `reactive()` to JSON strings, and not supporting the serialization of reactive variables generated by `ref()` to JSON strings.

```python: no-line-numbers
import simplejson

from reactivity import reactive, ref

a = reactive([reactive({'bar': 1})])
print(simplejson.dumps(a))  # will print: [{"bar": 1}]

b = reactive([ref({'bar': ref(1)})])
print(simplejson.dumps(b))  # Will raise an error: TypeError: Object is not JSON serializable
```

The solution to this problem is: you can first use the `deep_unref()` function (or `deepUnref()` function) to convert the reactive object to a regular Python object, and then serialize it to a JSON string:

```python: no-line-numbers
import simplejson

from reactivity import deep_unref, reactive, ref

obj = reactive([ref({'bar': ref(1)})])
print(simplejson.dumps(deep_unref(obj)))  # will print: [{"bar": 1}]
```