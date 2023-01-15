---
prev: ../quick-start
next: ./computed
---

# 响应式基础

**目录**

[[toc]]

## 声明响应式状态

我们可以使用 `reactive()` 函数创建一个响应式对象，它可以是 `dict`, `list`, `set` 或者其他任意类型的可变（mutable）实例对象：

```python:no-line-numbers
from reactivity import reactive

state = reactive({
    'count': 0
})
```

响应式对象的行为表现与普通的 Python 对象类似。不同之处在于 PyReactivity 能够跟踪对响应式对象的访问和修改操作。当响应式对象的状态发生变化时，PyReactivity 会自动更新与之相关的对象。

### 响应式对象 vs. 原始对象

值得注意的是，`reactive()` 返回的是一个原始对象的「响应式版本」，它和原始对象不是同一个对象：

```python:no-line-numbers
from reactivity import reactive

raw = {}
obj = reactive(raw)

# 原始对象的「响应式版本」和原始对象不是同一个对象
print(obj is raw)  # False
```

只有响应式对象才是响应式的，原始对象并不具有「响应式」的能力，更改原始对象的状态不会触发响应式对象的更新。因此，使用 PyReactivity 的响应式系统的最佳实践是 **仅使用响应式对象，避免直接使用原始对象**。

为保证访问响应式对象的一致性，对同一个原始对象调用 `reactive()` 会总是返回同样的响应式对象，而对一个已存在的响应式对象调用 `reactive()` 会返回其本身：

```python:no-line-numbers
print(reactive(raw) is obj)  # True
print(reactive(obj) is obj)  # True
```

这个规则对嵌套对象也适用。依靠深层响应性，响应式对象内的嵌套对象会被自动转换为响应式对象：

```python:no-line-numbers
obj = reactive({})
raw = {}
obj['nested'] = raw

print(obj['nested'] is raw)  # False
```

### `reactive()` 的局限性

`reactive()` API 有两条限制：

1. 仅对可变（mutable）对象有效（`dict`, `list`, `set` 等类型），而对 `str`、`int`、`float`、`bool` 等不可变（immutable）对象无效。
1. 因为 PyReactivity 的响应式系统是通过 **属性访问** 与 **索引访问（成员访问）** 进行追踪的，因此我们必须始终保持对该响应式对象的相同引用。这意味着我们不可以随意地「替换」一个响应式对象，因为这将导致对初始引用的响应性连接丢失：

```python:no-line-numbers
state = reactive({'count': 0})
# 上面的引用 ({ 'count': 0 }) 将不再被追踪（响应性连接已丢失！）
state = reactive({'count': 1})
```

同时这也意味着当我们将响应式对象的属性（attribute）或成员（membership）赋值至本地变量时，或是将该属性或成员传入一个函数时，我们会失去响应性：

```python:no-line-numbers
state = reactive({'count': 0})

# n 是一个局部变量，同 state['count'] 失去响应性连接
n = state['count']
# 不影响原始的 state
n += 1

# 该函数接收一个普通数字，并且将无法跟踪 state['count'] 的变化
call_some_function(state['count'])
```

## 用 `ref()` 定义响应式变量

`reactive()` 的种种限制归根结底是因为对于不可变对象来说，任何对对象本身产生修改的操作都会导致对象的引用发生变化，从而导致响应性连接丢失。因此，我们可以通过 `ref()` API 来定义一个响应式变量，该变量可以被赋值为任意类型的值，而不仅仅是可变对象：

```python:no-line-numbers
from reactivity import ref

count = ref(0)
```

`ref()` 将传入参数的值包装为一个带 `.value` 属性的 ref 对象：

```python:no-line-numbers
count = ref(0)

print(count)  # <Ref[int] value=0>
print(count.value)  # 0

count.value += 1
print(count.value)  # 1
```

和响应式对象的属性类似，ref 对象的 `.value` 属性也是响应式的。同时，当值为可变对象类型时，会用 `reactive()` 自动转换它的 `.value`。

一个包含对象类型值的 ref 可以响应式地替换整个对象：

```python:no-line-numbers
object_ref = ref({'count': 0})

# 这是响应式的替换
object_ref.value = {'count': 1}
```

ref 被传递给函数或是从一般对象上被赋值到新的变量时，不会丢失响应性：

```python:no-line-numbers
obj = {'foo': ref(1), 'bar': ref(2)}

# 该函数接受一个 ref 对象作为参数
# 需要通过 .value 取值
# 但她会保持响应性
call_some_function(obj['foo'])

# 仍然是响应式的
foo = obj['foo']
bar = obj['bar']
```

简而言之，`ref()` 让我们可以在任意类型的值上定义响应式变量，而不仅仅是可变对象。这意味着，我们可以创造一种对任意值的「引用」，并能够在不丢失响应性的前提下传递这些引用。这个功能很重要，利用该功能，我们可以在独立的函数中定义响应式变量，然后将其作为函数的返回值传递出去，并在其他地方使用它们。

### ref 在响应式对象中的解包

当一个 `ref` 被嵌套在一个响应式对象中，作为成员或属性被访问或更改时，它会被自动「解包」，因此会表现得和一般的属性一样，不需要使用 `.value`：

```python:no-line-numbers
count = ref(0)
state = reactive({
    'count': count,
})

# 这里并不需要使用 state['count'].value
# 直接使用 state['count'] 就可以
print(state['count'])  # 0

state['count'] = 1  # 相当于给 count.value 赋值
print(count.value)  # 1
```

如果将一个新的 ref 赋值给一个关联了已有 ref 的属性或成员，那么它会替换掉旧的 ref：

```python:no-line-numbers
other_count = ref(2)

state['count'] = other_count
print(state['count'])  # 2
# 原始 ref 现在已经和 state['count'] 失去联系
print(count.value)  # 1
```

### 序列类型的 ref 解包

注意，如果一个 ref 被嵌套在一个序列（如 `list`）类型的响应式对象中，它在被访问时不会被自动解包：

```python:no-line-numbers
books = reactive([ref('PyReactivity Guide')])
# 这里需要 .value
print(books[0].value)  # PyReactivity Guide
```
