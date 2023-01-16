---
prev: ./introduction
next: ./essentials/reactivity-fundamentals
---

# Quick Start

**Contents**

[[toc]]

## Installing PyReactivity

::: tip Prerequisites

- Familiarity with the command line
- [Python]((https://www.python.org/downloads/)) 3.6 or later version installed
:::

In this section, we will show you how to install PyReactivity in your project.

Make sure you have [Python 3.6 or later version](https://www.python.org/downloads/) installed, then enter the following command in the command line (without the `>` symbol):

```bash:no-line-numbers
> pip install pyreactivity
```

In an ideal situation, the command above will call the pip command of your current Python environment and install the latest version of PyReactivity into your project.

During the installation process, you may see some output from pip. If the installation is successful, you will see output similar to the following:

```bash:no-line-numbers
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Collecting pyreactivity
  Using cached https://pypi.tuna.tsinghua.edu.cn/packages/8d/7b/06df0fa946a4cab56c29fd604f245433b8f4374fc383f40d888cfeca4650/pyreactivity-0.0.1-py3-none-any.whl (19 kB)
Installing collected packages: pyreactivity
Successfully installed pyreactivity-0.0.1
```

In some rare cases, you may need to use the pip3 command to install PyReactivity, or use the python -m pip command to install PyReactivity. And you may need to add the -U flag to ensure you are installing the latest version of PyReactivity. In these cases, you can use the following commands:

```bash:no-line-numbers
> pip3 install -U pyreactivity
```

Or

```bash:no-line-numbers
> python -m pip install -U pyreactivity
```

However, these cases are very rare. In most cases, you only need to simply use the `pip install pyreactivity` command to install PyReactivity.

::: warning Note
If you have multiple versions of Python environments installed on your computer, make sure that the Python environment you are using to install PyReactivity is the same as the one used in your project. Otherwise, you may encounter some strange issues (such as not being able to import the PyReactivity module after installation).
:::

## Importing PyReactivity

In this section, we will discuss how to import PyReactivity in your project.

You can use the following command to import PyReactivity and test if the installation was successful:

```python:no-line-numbers
# Import the ref() and reactive() functions as an example
from reactivity import ref, reactive

a = ref(1)
print(f'a is {a.value}')

b = reactive({
    'c': 2
})
print(f'b["c"] is {b["c"]}')
```

If everything goes well, running the code will give you the following output:

```bash:no-line-numbers
a is 1
b["c"] is 2
```

Of course, you can also use `from reactivity import *` to import all PyReactivity API functions, but we do not recommend it as it can pollute your namespace.

## Reactivity Fundamentals

Now that you've successfully installed and imported PyReactivity, you may not know how to use it or understand what "reactive programming" is.

Don't worry, next, you can read [Reactivity Fundamentals](./essentials/reactivity-fundamentals.md) to learn the basics of PyReactivity. We will introduce how to use PyReactivity to implement reactive programming in Python.
