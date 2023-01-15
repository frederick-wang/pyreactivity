---
next: ./quick-start
---

# 简介

## 什么是 PyReactivity？

PyReactivity 是一个在 Python 中实现了「响应性」功能的库，它的目标是让你能够在 Python 中使用类似 Vue.js 的响应式编程。

和 Vue.js 一样，PyReactivity 提供了一套低侵入性的响应式系统。通过使用 PyReactivity，你可以在 Python 中体验「响应式编程」，而不需要学习新的语法，也不需要使用一些复杂的库。

你可以用响应式的 Python 对象组成复杂的状态，PyReactivity 会自动跟踪 Python 对象的状态并在其发生变化时响应式地更新与之相关的对象，这让状态管理更加简单直观。

你可能已经有了些疑问——先别急，在后续的文档中我们会详细介绍每一个细节。

## 什么是响应性？

这个术语在今天的各种编程讨论中经常出现，但人们说它的时候究竟是想表达什么意思呢？本质上，响应性是一种可以使我们声明式地处理变化的编程范式。一个经常被拿来当作典型例子的用例即是 Excel 表格：

<!-- ![](https://res.zhaoji.ac.cn/images/20230115061800.png) -->

<p style="text-align: center">
  <img src="https://res.zhaoji.ac.cn/images/20230115061800.png" alt="image-20210115061800388" style="width: 50%" />
</p>

这里单元格 A2 中的值是通过公式 `= A0 + A1` 来定义的，因此最终得到的值为 3。

在 Excel 中，如果你试着更改 A0 或 A1，A2 也会随即自动更新。

但是，在 Python 中，并没有这样的功能。如果我们用 Python 编写类似的逻辑：

```python:no-line-numbers
A0 = 1
A1 = 2
A2 = A0 + A1

print(A2)  # 3

A0 = 2
print(A2)  # 仍然是 3
```

当我们更改 `A0` 后，`A2` 不会自动更新。

像 Excel 中那样，当一个值发生变化时，其它相关的值也会自动更新，这就是响应性。而在 Python 中，我们可以使用 PyReactivity 来实现这种响应性：

```python:no-line-numbers
from reactivity import ref, computed

A0 = ref(1)
A1 = ref(2)
A2 = computed(lambda: A0.value + A1.value)

print(A2.value)  # 打印 3

A0.value = 2
print(A2.value)  # 打印 4
```

您可以阅读 [快速上手](quick-start.md) 来了解如何使用 PyReactivity。

## Github 仓库

PyReactivity 的代码托管在 Github 上，你可以在 [frederick-wang/pyreactivity](https://github.com/frederick-wang/pyreactivity) 仓库中找到它的全部源代码，包括具体实现、单元测试、文档和示例。

## 参与贡献

PyReactivity 是一个开源项目，欢迎任何人参与贡献。如果你有任何问题或建议，欢迎在 [Github Issues](https://github.com/frederick-wang/pyreactivity/issues) 中提出。

## 鸣谢

PyReactivity 的灵感来自于 Vue.js，它的实现也参考了 Vue.js 的源代码。感谢 Vue.js 团队的无私奉献。

本文档亦大量参考了 Vue.js 的文档，感谢 Vue.js 文档编写者的无私奉献。
