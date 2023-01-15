---
prev: ./reactivity-fundamentals
next: ./watchers
---

# 计算属性

**目录**

[[toc]]

## 基础示例

`computed()` 可以根据一个函数（function）创建出一个只读的 ref 对象，该 ref 的值为函数的返回值，我们称该 ref 为一个 **计算属性**。如果在这个函数中包含响应式对象参与运算，那么这个计算属性将会在这些响应式对象发生变化时自动更新。

比如说，我们有一个包含嵌套数组的响应式字典：

```python:no-line-numbers
from reactivity import reactive

author = reactive({
    'name': 'Zhang San',
    'books': [
        'Advanced Guide',
        'Basic Guide',
    ]
})
```

我们想根据 author 是否已有一些书籍来展示不同的信息，该信息存储在 `message` 变量中。如果不使用计算属性，我们需要每次修改 `author['books']` 后手动更新 `message` 的值，这十分麻烦：

```python:no-line-numbers
message = ''


def update_message():
    global message

    name = author['name']
    book_num = len(author['books'])

    if book_num:
        message = f'{name}, you have {book_num} books.'
    else:
        message = f'{name}, you have no books.'


update_message()
print(message)  # Zhang San, you have 2 books.

author['books'].pop()
update_message()
print(message)  # Zhang San, you have 1 books.

author['books'].pop()
update_message()
print(message)  # Zhang San, you have no books.
```

因此，我们推荐使用 **计算属性** 来描述依赖响应式状态的复杂逻辑，这是重构后的示例：

```python:no-line-numbers
from reactivity import computed, reactive

author = reactive({
    'name': 'Zhang San',
    'books': [
        'Advanced Guide',
        'Basic Guide',
    ]
})


def update_message():
    name = author['name']
    book_num = len(author['books'])

    if book_num:
        return f'{name}, you have {book_num} books.'
    else:
        return f'{name}, you have no books.'

# 一个计算属性 ref
message = computed(update_message)
print(message.value)  # Zhang San, you have 2 books.

author['books'].pop()
print(message.value)  # Zhang San, you have 1 books.

author['books'].pop()
print(message.value)  # Zhang San, you have no books.
```

我们这里定义了一个计算属性 `message`。`computed()` 函数期望接收一个 getter 函数作为参数，返回值为一个 **计算属性 ref**。和普通的 ref 一样，你可以通过 `message.value` 访问计算结果。

PyReactivity 的计算属性会自动追踪响应式依赖，它会检测到 `message` 依赖于 `author['books']`，因此当 `author['books']` 发生变化时，`message` 也会自动更新。

类似的，如果有其他响应式变量依赖于 `message`，那么当 `message` 被更新时，这些变量也会自动更新。

## 计算属性的缓存

你可能会注意到，直接调用 `update_message()` 函数就可以获得和 `message.value` 一样的结果，那我们为什么还要使用计算属性呢？

这是因为 `update_message()` 函数并没有 **缓存结果**，每次调用都会重新计算一次。而计算属性会自动缓存结果，只有当其响应式依赖更新时才重新计算。这意味着只要 `author['books']` 不改变，无论多少次访问 `message` 都会立即返回先前的计算结果，而不用重复执行 `update_message()` 函数。

为什么需要缓存呢？想象一下我们有一个非常耗性能的计算属性 `foo`，需要循环一个巨大的列表并做许多计算逻辑，并且可能也有其他计算属性依赖于 `foo`。没有缓存的话，我们会重复执行非常多次 `foo` 的 getter 函数，然而这实际上没有必要！如果你确定不需要缓存，那么也可以使用方法调用。

## 注意

### Getter 函数不应有副作用

计算属性的 getter 应只做计算而没有任何其他的副作用，这一点非常重要，请务必牢记，不要在 getter 函数中修改 getter 函数之外的值！

一个计算属性的声明中描述的是如何根据其他值派生一个值。因此 getter 的职责应该仅为计算和返回该值。在之后的指引中我们会讨论如何使用监听器根据其他响应式状态的变更来运行造成副作用的代码。

### 无法直接修改计算属性值

从计算属性返回的值是 **派生状态**。可以把它看作是一个「临时快照」，每当源状态发生变化时，就会创建一个新的快照。

更改快照是没有意义的，因此计算属性的返回值是只读的，永远不应该被更改——应该更新它所依赖的源状态以触发新的计算。
