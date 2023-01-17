---
prev: ../essentials/watchers
---

# JSON 序列化

**目录**

[[toc]]

在交换数据时，我们经常会将 Python 中的数据对象序列化为 JSON 格式的字符串。

## `json.dumps()` 和 `json.dump()`

如果是你使用的是 Python 内建的 `json` 模块，那么你不需要做任何额外操作，就可以 **直接** 用 `json.dumps` 将响应式对象序列化为 JSON 字符串。

```python:no-line-numbers
import json

from reactivity import reactive, ref

obj = reactive({'foo': ref({'bar': [ref(1), 2, 3]})})
print(json.dumps(obj))  # 将会打印：{"foo": {"bar": [1, 2, 3]}}
```

不论是使用 `reactive()` 生成的响应式对象，还是用 `ref()` 生成的响应式变量，它们都可以直接被 `json.dumps()` 序列化为 JSON 字符串。

如果你需要对自定义对象进行序列化，一般会定义 `json.dumps` 的 `default` 参数或者 `cls` 参数。**不用担心设置这两个参数会与 PyReactivty 冲突，PyReactivity 与它们是兼容的。**

例如，我们需要自定义一个能将 `complex` 类型的复数对象序列化的 `default` 函数，调用 `json.dumps` 后可以得到正确的结果：

```python:no-line-numbers
def complex_handler(obj):
    if isinstance(obj, complex):
        return [obj.real, obj.imag]
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

obj = ref({'foo': ref({'bar': [ref(1), 2, 3]}), 'baz': ref(1 + 1j), 'c': 2 + 1j})
print(json.dumps(obj, default=complex_handler))
# 将会打印：{"foo": {"bar": [1, 2, 3]}, "baz": [1.0, 1.0], "c": [2.0, 1.0]}
```

如果你更喜欢用设置 `cls` 参数的方式来定制编码器，也同样是兼容的：

```python:no-line-numbers
class ComplexEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, complex):
            return [obj.real, obj.imag]
        return json.JSONEncoder.default(self, obj)

obj = ref({'foo': ref({'bar': [ref(1), 2, 3]}), 'baz': ref(1 + 1j), 'c': 2 + 1j})
print(json.dumps(obj, cls=ComplexEncoder))
# 将会打印：{"foo": {"bar": [1, 2, 3]}, "baz": [1.0, 1.0], "c": [2.0, 1.0]}
```

## 实现原理

在 `reactivity` 模块被第一次导入时，PyReactivity 会替换 `json.dump()` 和 `json.dumps()` 两个方法，使其可以序列化响应式对象。

如果你想手动控制这个过程，可以从 `reactivity.patches` 中导入 `patch_json()` 与 `unpatch_json()` 两个函数，分别用于替换与恢复 `json.dump()` 和 `json.dumps()` 两个方法。

如果调用了 `unpatch_json()`，那么 `json.dumps()` 将无法序列化响应式对象：

```python:no-line-numbers
from reactivity import ref

from reactivity.patches import patch_json, unpatch_json

a = ref(1)

unpatch_json()
print(json.dumps(a))  # 将会报错：TypeError: Object is not JSON serializable
```

如果在调用了 `unpatch_json()` 后，又调用了 `patch_json()`，那么 `json.dumps()` 将重新具有序列化响应式对象的能力：

```python:no-line-numbers
from reactivity import ref

from reactivity.patches import patch_json, unpatch_json

a = ref(1)

unpatch_json()
patch_json()
print(json.dumps(a))  # 将会打印：1
```

## 第三方 JSON 库

如果你使用的是第三方的 JSON 库，例如 `simplejson`，那么它们默认只支持将 `reactive()` 生成的响应式对象序列化为 JSON 字符串，而不支持将 `ref()` 生成的响应式变量序列化为 JSON 字符串。

```python: no-line-numbers
import simplejson

from reactivity import reactive, ref

a = reactive([reactive({'bar': 1})])
print(simplejson.dumps(a))  # 将会打印：[{"bar": 1}]

b = reactive([ref({'bar': ref(1)})])
print(simplejson.dumps(b))  # 将会报错：TypeError: Object is not JSON serializable
```

这个问题的解决方案是：你可以先用 `deep_unref()` 函数（或 `deepUnref()` 函数）将响应式对象转换为普通 Python 对象，然后再将其序列化为 JSON 字符串：

```python: no-line-numbers
import simplejson

from reactivity import deep_unref, reactive, ref

obj = reactive([ref({'bar': ref(1)})])
print(simplejson.dumps(deep_unref(obj)))  # 将会打印：[{"bar": 1}]
```
