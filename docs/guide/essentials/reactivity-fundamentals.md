---
prev: ../quick-start
next: ./computed
---

# Reactive Fundamentals

**Contents**

[[toc]]

## Declaring Reactive State

We can use the `reactive()` function to create a reactive object, which can be a `dict`, `list`, `set`, or any other type of mutable instance object.

```python:no-line-numbers
from reactivity import reactive

state = reactive({
    'count': 0
})
```

Reactive objects behave similarly to regular Python objects. The difference is that PyReactivity can track access and modification operations on reactive objects. When the state of a reactive object changes, PyReactivity will automatically update any related objects.

### Reactive Objects vs. Raw Objects

It is worth noting that the `reactive()` function returns the "reactive version" of the raw object, which is not the same object as the raw object:

```python:no-line-numbers
from reactivity import reactive

raw = {}
obj = reactive(raw)

# The "reactive version" of the raw object and the raw object are not the same object
print(obj is raw)  # False
```

Only reactive objects are reactive, raw objects do not have the "reactive" ability, and changing the state of a raw object will not trigger an update of the reactive object. Therefore, the best practice when using the PyReactivity's reactive system is to **only use reactive objects and avoid directly using raw objects**.

To ensure consistency when accessing reactive objects, calling `reactive()` on the same raw object will always return the same reactive object, and calling `reactive()` on an existing reactive object will return itself:

```python:no-line-numbers
print(reactive(raw) is obj)  # True
print(reactive(obj) is obj)  # True
```

This rule also applies to nested objects. Through deep reactivity, nested objects within a reactive object will be automatically converted to reactive objects：

```python:no-line-numbers
obj = reactive({})
raw = {}
obj['nested'] = raw

print(obj['nested'] is raw)  # False
```

### Limitations of `reactive()`

The `reactive()` API has two limitations:

1. It is only effective for mutable objects (`dict`, `list`, `set`, etc.) and not for immutable objects such as `str`, `int`, `float`, `bool`, etc.
1. Because PyReactivity's reactive system is tracked through **property access** and **index access (membership access)**, we must always maintain the same reference to the reactive object. This means that we cannot easily "replace" a reactive object, as this will result in the loss of reactivity connection to the initial reference:

```python:no-line-numbers
state = reactive({'count': 0})
# The above reference ({'count': 0}) will no longer be tracked (reactivity connection is lost!)
state = reactive({'count': 1})
```

This also means that when we assign a reactive object's attribute or member to a local variable or pass it as an argument to a function, we will lose reactivity:

```python:no-line-numbers
state = reactive({'count': 0})

# n is a local variable, and loses reactivity connection with state['count']
n = state['count']
# Does not affect the original state
n += 1

# The function accepts a regular number and will not be able to track changes to state['count']
call_some_function(state['count'])
```

## Defining Reactive Variables with `ref()`

The limitations of `reactive()` ultimately stem from the fact that for immutable objects, any operation that modifies the object itself will result in a change of the object's reference, resulting in the loss of reactivity connection. Therefore, we can use the `ref()` API to define a reactive variable that can be assigned any type of value, not just mutable objects:

```python:no-line-numbers
from reactivity import ref

count = ref(0)
```

`ref()` wraps the value passed as an argument in a ref object with a `.value` property：

```python:no-line-numbers
count = ref(0)

print(count)  # <Ref[int] value=0>
print(count.value)  # 0

count.value += 1
print(count.value)  # 1
```

Like the properties of reactive objects, the `.value` property of ref objects is also reactive. Additionally, when the value is a mutable object type, it will automatically be converted using `reactive()` for its `.value`.

A ref containing an object type value can replace the whole object reactively.

```python:no-line-numbers
object_ref = ref({'count': 0})

#This is a reactive replacement
object_ref.value = {'count': 1}
```

Refs passed to a function or assigned to a new variable from a regular object do not lose reactivity:

```python:no-line-numbers
obj = {'foo': ref(1), 'bar': ref(2)}

# The function accepts a ref object as an argument,
# it needs to be accessed by .value
# but it will maintain reactivity
call_some_function(obj['foo'])

#Still reactive
foo = obj['foo']
bar = obj['bar']
```

In summary, `ref()` allows us to define reactive variables on any type of value, not just mutable objects. This means that we can create a "reference" to any value and pass it around without losing reactivity. This feature is important as it allows us to define reactive variables in independent functions and then pass them out as return values, to be used elsewhere.

### Unpacking ref in a reactive object

When a `ref` is nested in a reactive object, as a member or property, it will be automatically 'unwrapped' when accessed or modified. This means that it behaves like a regular property and you don't have to use `.value`：

```python:no-line-numbers
count = ref(0)
state = reactive({
    'count': count,
})

# You don't need to use state['count'].value here,
# you can just use state['count']
print(state['count'])  # 0

state['count'] = 1 # This is equivalent to assigning to count.value
print(count.value)  # 1
```

If a new ref is assigned to a property or member that is associated with an existing ref, the old ref will be replaced:

```python:no-line-numbers
other_count = ref(2)

state['count'] = other_count
print(state['count'])  # 2
# The original ref is now disconnected from state['count']
print(count.value)  # 1
```

### Unpacking ref in a sequence type

Note that if a ref is nested within a sequence (such as a `list`) type of reactive object, it will not be automatically unpacked when accessed:

```python:no-line-numbers
books = reactive([ref('PyReactivity Guide')])
# .value is required here
print(books[0].value)  # PyReactivity Guide
```
