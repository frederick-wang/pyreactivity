---
next: ./quick-start
---

# Introduction

## What is PyReactivity?

PyReactivity is a library in Python that implements "reactivity" functionality, with the goal of allowing you to use reactive programming similar to Vue.js in Python.

Like Vue.js, PyReactivity provides a low-invasive reactive system. By using PyReactivity, you can experience "reactive programming" in Python without learning new syntax or using complex libraries.

You can compose complex states with reactive Python objects and PyReactivity will automatically track the state of the Python objects and respond reactively to updates of related objects, making state management more simple and intuitive.

You may have some questions now - don't worry, we will detail every aspect in the following documentation.

## What is reactivity?

This term is often seen in various programming discussions today, but what exactly do people mean when they say it? Essentially, reactivity is a programming paradigm that allows us to handle changes in a declarative manner. A commonly cited example is an Excel spreadsheet:

<!-- ![](https://res.zhaoji.ac.cn/images/20230115061800.png) -->

<p style="text-align: center">
  <img src="https://res.zhaoji.ac.cn/images/20230115061800.png" alt="image-20210115061800388" style="width: 50%" />
</p>

In the case of Excel, cell A2 has a value defined by the formula = A0 + A1 , therefore its final value is 3.

If you try to change the value of A0 or A1 in Excel, A2 will automatically update.

But in Python, this functionality is not built-in. If we were to write similar logic in Python:

```python:no-line-numbers
A0 = 1
A1 = 2
A2 = A0 + A1

print(A2)  # 3

A0 = 2
print(A2)  # still 3
```

As we can see in the example, when we change the value of `A0`, the value of `A2` does not update automatically.

Like in Excel, where when one value changes, other related values update automatically, this is called reactivity. In Python, we can use PyReactivity library to achieve this reactivity feature.

```python:no-line-numbers
from reactivity import ref, computed

A0 = ref(1)
A1 = ref(2)
A2 = computed(lambda: A0.value + A1.value)

print(A2.value)  # print 3

A0.value = 2
print(A2.value)  # print 4
```

You can read the [Quick Start](quick-start.md) to learn how to use PyReactivity.

## Github Repository

The code for PyReactivity is hosted on Github, you can find the full source code including implementation details, unit tests, documentation, and examples in the [frederick-wang/pyreactivity](https://github.com/frederick-wang/pyreactivity) repository.

## Contributing

PyReactivity is an open-source project and welcomes any contributions. If you have any issues or suggestions, feel free to raise them in the [Github Issues](https://github.com/frederick-wang/pyreactivity/issues).

## Acknowledgments

PyReactivity is inspired by Vue.js and its implementation also references the source code of Vue.js. Thanks to the Vue.js team for their selfless dedication.

This documentation also heavily references the documentation of Vue.js, thanks to the document writers of Vue.js for their selfless dedication.
