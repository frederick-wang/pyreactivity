---
prev: ./introduction
next: ./essentials/reactivity-fundamentals
---

# 快速上手

**目录**

[[toc]]

## 安装 PyReactivity

::: tip 前提条件

- 熟悉命令行
- 已安装 3.6 或更高版本的 [Python](https://www.python.org/downloads/)
:::

在本节中，我们将介绍如何在你的项目中安装 PyReactivity。

确保你已经安装了 [Python 3.6 或更高版本](https://www.python.org/downloads/)，然后在命令行中输入以下命令（不要带上 `>` 符号）：

```bash:no-line-numbers
> pip install pyreactivity
```

在理想情况下，上面的命令将会调用当前 Python 环境的 `pip` 命令，然后安装最新版的 PyReactivity 到你的项目中。

安装过程中，你可能会看到一些 `pip` 的输出信息。如果安装成功，你将会看到类似下面的输出：

```bash:no-line-numbers
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Collecting pyreactivity
  Using cached https://pypi.tuna.tsinghua.edu.cn/packages/8d/7b/06df0fa946a4cab56c29fd604f245433b8f4374fc383f40d888cfeca4650/pyreactivity-0.0.1-py3-none-any.whl (19 kB)
Installing collected packages: pyreactivity
Successfully installed pyreactivity-0.0.1
```

在一些罕见的特殊情况下，你可能需要使用 `pip3` 命令来安装 PyReactivity，或者使用 `python -m pip` 命令来安装 PyReactivity。并且可能需要添加 `-U` 参数来确保安装最新版的 PyReactivity。这时你可以使用以下命令：

```bash:no-line-numbers
> pip3 install -U pyreactivity
```

或者

```bash:no-line-numbers
> python -m pip install -U pyreactivity
```

不过，这些情况都是非常罕见的。在大多数情况下，你只需要简单的使用 `pip install pyreactivity` 命令来安装 PyReactivity。

::: warning 注意
如果你的电脑上安装了多个版本的 Python 环境，请确保你当前安装 PyReactivity 的 Python 环境是你的项目所使用的 Python 环境。否则，你可能会遇到一些奇怪的问题（如：安装后无法导入 PyReactivity 模块）。
:::

## 导入 PyReactivity

在本节中，我们将介绍如何在你的项目中导入 PyReactivity。

你可以使用以下命令来导入 PyReactivity，测试一下是否安装成功：

```python:no-line-numbers
# 以导入 ref() 和 reactive() 函数为例
from reactivity import ref, reactive

a = ref(1)
print(f'a 的值为：{a.value}')

b = reactive({
    'c': 2
})
print(f'b["c"] 的值为：{b["c"]}')
```

如果一切顺利，运行代码后你将会看到如下所示的输出：

```bash:no-line-numbers
a 的值为：1
b["c"] 的值为：2
```

当然，你也可以使用 `from reactivity import *` 来导入所有的 PyReactivity API 函数。但是，我们不推荐这么做，因为这样会污染你的命名空间。

## 响应式基础

现在，你已经成功安装并测试导入了 PyReactivity，但是你可能还不知道如何使用 PyReactivity，也并不了解什么是「响应式编程」。

别担心，接下来，你可以阅读 [响应式基础](./essentials/reactivity-fundamentals.md) 来了解 PyReactivity 的基础知识。我们将会介绍如何使用 PyReactivity 来实现 Python 中的响应式编程。
