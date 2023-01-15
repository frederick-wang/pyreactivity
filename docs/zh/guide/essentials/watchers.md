---
prev: ./computed
---

# 侦听器

**目录**

[[toc]]

## 基本示例

计算属性允许我们声明性地计算衍生值。然而在有些情况下，我们需要在状态变化时执行一些「副作用」。这就是侦听器的用武之地。

::: tip 「副作用」是什么？

在计算机科学中，函数副作用指当调用函数时，除了返回可能的函数值之外，还对主调用函数产生附加的影响。例如修改全局变量（函数外的变量），修改参数，向主调方的终端、管道输出字符或改变外部存储信息等。
:::

我们可以使用 `watch()` 函数在每次响应式状态发生变化时触发 **回调函数**。

```python:no-line-numbers
from reactivity import ref, watch

foo = ref(1)

# 可以直接侦听一个 ref
watch(
    foo,
    lambda new, old: print(f"foo changed from {old} to {new}"),
)

foo.value += 1  # 将打印 "foo changed from 1 to 2"
foo.value = 10  # 将打印 "foo changed from 2 to 10"
```

可以看到，当 `foo` 的值发生变化时，回调函数会被触发，调用 `print()` 打印。回调函数的参数数量是可变的：

- 如果没有参数，回调函数会在每次触发时被调用。
- 如果只有一个参数，回调函数会在每次触发时被调用，并且参数是 **新值**。
- 如果有两个参数，回调函数会在每次触发时被调用，并且两个参数分别是 **新值** 和 **旧值**。


## 侦听数据源类型

`watch()` 的第一个参数可以是不同形式的「数据源」：它可以是一个 ref (包括计算属性)、一个响应式对象、一个 getter 函数、或多个数据源组成的序列（如 `list`）：

```python:no-line-numbers
x = ref(0)
y = ref(0)

# 单个 ref
watch(x, lambda new_x: print(f'x is {new_x}'))

# getter 函数
watch(
    lambda: x.value + y.value,
    lambda s: print(f'sum of x + y is: {s}'),
)


# 多个来源组成的序列
def callback(new_vals):
    new_x, new_y = new_vals
    print(f'x is {new_x} and y is {new_y}')


watch([x, lambda: y.value], callback)

x.value += 1
# 将输出：
# x is 1 and y is 0
# sum of x + y is: 1
# x is 1
y.value += 1
# 将输出：
# x is 1 and y is 1
# sum of x + y is: 2
```

注意，你不能直接侦听响应式对象的成员值，例如:

```python:no-line-numbers
obj = reactive({'count': 0})

# 错误，因为 watch() 得到的参数是一个 int 类型，而不是一个 ref 类型
watch(obj['count'], lambda count: print(f'count is: {count}'))
```

如果你运行上面的代码，将得到一个错误信息： `TypeError: Invalid watch source type: <class 'int'> for watch().`。

那如果我们想侦听响应式对象的成员值，该怎么办呢？这里需要用一个返回该属性的 getter 函数：

```python:no-line-numbers
# 提供一个 getter 函数
watch(
    lambda: obj['count'],
    lambda count: print(f'count is: {count}'),
)
```

## 深层侦听器

直接给 `watch()` 传入一个响应式对象，会隐式地创建一个深层侦听器——该回调函数在所有嵌套的变更时都会被触发：

```python:no-line-numbers
state = reactive({'foo': {'bar': 1}})

# 提供一个 getter 函数
watch(
    state,
    # 在嵌套的属性变更时触发
    # 注意：`new` 此处和 `old` 是相等的
    # 因为它们是同一个对象！
    lambda new, old: print(f'state changed: {old} -> {new}'),
)

state['foo']['bar'] += 1
# 将打印：state changed: {'foo': {'bar': 2}} -> {'foo': {'bar': 2}}
```

相比之下，一个返回响应式对象的 getter 函数，只有在返回不同的对象时，才会触发回调：

```python:no-line-numbers
state = reactive({'foo': {'bar': 1}})

# 提供一个 getter 函数
watch(
    lambda: state,
    # 在嵌套的属性变更时，不会触发
    lambda new, old: print(f'state changed: {old} -> {new}'),
)

state['foo']['bar'] += 1  # 什么都不会打印
```

你也可以给上面这个例子显式地加上 `deep` 关键字参数，强制转成深层侦听器：

```python:no-line-numbers
state = reactive({'foo': {'bar': 1}})

# 提供一个 getter 函数
watch(
    lambda: state,
    lambda new, old: print(f'state changed: {old} -> {new}'),
    # 因为设置了 deep=True，所以在嵌套的属性变更时会触发
    deep=True,
)

state['foo']['bar'] += 1
# 将打印：state changed: {'foo': {'bar': 2}} -> {'foo': {'bar': 2}}
```

::: warning 谨慎使用
深度侦听需要遍历被侦听对象中的所有嵌套的属性和成员，当用于大型数据结构时，开销很大。因此请只在必要时才使用它，并且要留意性能。
:::

## watch_effect() / watchEffect()

`watch()` 是懒执行的：仅当数据源变化时，才会执行回调。但在某些场景中，我们希望在创建侦听器时，立即执行一遍回调。这时，可以使用 `watch_effect()`：

```python:no-line-numbers
from reactivity import ref, watch_effect

foo = ref(1)

watch_effect(lambda: print(f"foo is {foo.value}"))
# 将立即打印 "foo is 1"

foo.value += 1  # 将打印 "foo is 2"
```

这个例子中，回调会立即执行。在执行期间，它会自动追踪 `foo.value` 作为依赖（和计算属性的行为类似）。每当 `foo.value` 变化时，回调会再次执行。

如果比起蛇形命名法（snake_case，又叫下划线命名法），你更喜欢驼峰命名法（camelCase），那么可以使用 `watchEffect()`，它们两个函数是完全相同的：

```python:no-line-numbers
from reactivity import watchEffect
```

## `watch` vs. `watch_effect`

`watch` 和 `watch_effect` 都能响应式地执行有副作用的回调。它们之间的主要区别是追踪响应式依赖的方式：

- `watch` 只追踪明确侦听的数据源。它不会追踪任何在回调中访问到的东西。另外，仅在数据源确实改变时才会触发回调。`watch` 会避免在发生副作用时追踪依赖，因此，我们能更加精确地控制回调函数的触发时机。
- `watch_effect`，则会在副作用发生期间追踪依赖。它会在同步执行过程中，自动追踪所有能访问到的响应式属性。这更方便，而且代码往往更简洁，但有时其响应性依赖关系会不那么明确。

## 停止侦听器

在大多数情况下，我们不需要手动停止侦听器。但是，如果你确实需要手动停止侦听器，可以调用 `watch` 或 `watch_effect` **返回的函数**：

```python:no-line-numbers
unwatch = watch_effect(lambda: None)

# ... 当该侦听器不再需要时
unwatch()
```
