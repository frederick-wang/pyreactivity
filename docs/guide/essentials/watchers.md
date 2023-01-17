---
prev: ./computed
next: ../tips/json-serialization
---

# Watchers

**Contents**

[[toc]]

## Basic Example

Computed properties allow us to declare calculations of derived values. However, in some cases, we need to perform some "side effects" when the state changes. This is where watchers come into play.

::: tip What are "side effects"?

In computer science, a function side effect refers to additional effects on the main calling function besides the possible function value returned when the function is called. Examples include modifying global variables (variables outside the function), modifying parameters, outputting characters to the main caller's terminal or pipe, or changing external storage information.
:::

We can use the `watch()` function to trigger a **callback function** every time a reactive state changes.

```python:no-line-numbers
from reactivity import ref, watch

foo = ref(1)

# Can directly watch to a ref
watch(
    foo,
    lambda new, old: print(f"foo changed from {old} to {new}"),
)

foo.value += 1  # Will print "foo changed from 1 to 2"
foo.value = 10  # Will print "foo changed from 2 to 10"
```

The callback function can be triggered when the value of `foo` changes, calling `print()` to print the output. The number of parameters for the callback function is variable:

- If there are no parameters, the callback function will be called each time it is triggered.
- If there is only one parameter, the callback function will be called each time it is triggered and the parameter is the **new value**.
- If there are two parameters, the callback function will be called each time it is triggered and the two parameters are respectively the **new value** and **old value**.

## Types of Data Sources that can be Watched

The first parameter of `watch()` can take different forms of 'data source': it can be a ref (including computed properties), a reactive object, a getter function, or a sequence of multiple data sources (such as a `list`):

```python:no-line-numbers
x = ref(0)
y = ref(0)

# Single ref
watch(x, lambda new_x: print(f'x is {new_x}'))

# getter function
watch(
    lambda: x.value + y.value,
    lambda s: print(f'sum of x + y is: {s}'),
)


# Sequence of multiple sources
def callback(new_vals):
    new_x, new_y = new_vals
    print(f'x is {new_x} and y is {new_y}')


watch([x, lambda: y.value], callback)

x.value += 1
# will print:
# x is 1 and y is 0
# sum of x + y is: 1
# x is 1
y.value += 1
# will print:
# x is 1 and y is 1
# sum of x + y is: 2
```

Note that you cannot directly watch the member values of a reactive object, for example:

```python:no-line-numbers
obj = reactive({'count': 0})

# Error, because watch() receives a parameter of type int, not a ref type.
watch(obj['count'], lambda count: print(f'count is: {count}'))
```

If you run the code above, you will get an error message: `TypeError: Invalid watch source type: <class 'int'> for watch().`。

If we want to watch to the member value of a reactive object, what should we do? Here we need to use a getter function that returns that property:

```python:no-line-numbers
# Provide a getter function
watch(
    lambda: obj['count'],
    lambda count: print(f'count is: {count}'),
)
```

## Deep Watchers

Passing a reactive object directly to the `watch()` function will implicitly create a deep watcher - the callback function will be triggered on all nested changes:

```python:no-line-numbers
state = reactive({'foo': {'bar': 1}})

# Provide a getter function
watch(
    state,
    # Triggers on nested property changes
    # Note: `new` and `old` here are the same
    # because they are the same object!
    lambda new, old: print(f'state changed: {old} -> {new}'),
)

state['foo']['bar'] += 1
# Prints: state changed: {'foo': {'bar': 2}} -> {'foo': {'bar': 2}}
```

In contrast, a getter function that returns a reactive object will only trigger the callback when a different object is returned:

```python:no-line-numbers
state = reactive({'foo': {'bar': 1}})

# Provide a getter function
watch(
    lambda: state,
    # Does not trigger on nested property changes
    lambda new, old: print(f'state changed: {old} -> {new}'),
)

state['foo']['bar'] += 1  # Nothing will be printed
```

You can also explicitly add the `deep` keyword argument to the above example to force it to be a deep watcher:

```python:no-line-numbers
state = reactive({'foo': {'bar': 1}})

# Provide a getter function
watch(
    lambda: state,
    lambda new, old: print(f'state changed: {old} -> {new}'),
    # Because deep=True is set, it will trigger on nested property changes
    deep=True,
)

state['foo']['bar'] += 1
# Prints: state changed: {'foo': {'bar': 2}} -> {'foo': {'bar': 2}}
```

::: warning Use with caution
Deep watching requires traversing all nested properties and members within the watched object, which can be costly when used on large data structures. Therefore, use it only when necessary and be mindful of performance.
:::

## watch_effect() / watchEffect()

The `watch()` function is lazy-executed, it only triggers the callback when the data source changes. However, in certain scenarios, we may want the callback to be executed immediately upon creating the watcher. In such cases, we can use `watch_effect()`:

```python:no-line-numbers
from reactivity import ref, watch_effect

foo = ref(1)

watch_effect(lambda: print(f"foo is {foo.value}"))
# Will immediately print "foo is 1"

foo.value += 1  # Will print "foo is 2"
```

In this example, the callback is executed immediately. During execution, it automatically tracks `foo.value` as a dependency (similar to the behavior of computed properties). The callback will be executed again every time `foo.value` changes.

If you prefer camelCase naming convention instead of snake_case, you can use `watchEffect()`, which is the same function as watch_effect().

```python:no-line-numbers
from reactivity import watchEffect
```

## `watch` vs. `watch_effect`

Both `watch` and `watch_effect` can execute callbacks with side-effects reactively. The main difference between them is how they track reactive dependencies:

- `watch` only tracks the explicitly watched data source. It does not track anything accessed within the callback. Also, it only triggers the callback when the data source actually changes. `watch` avoids tracking dependencies during side-effects, so we can have more control over when the callback function is triggered.
- `watch_effect` instead tracks dependencies during side-effects. It automatically tracks all reactive properties accessed during the synchronous execution, which is more convenient and often results in more concise code, but sometimes the reactive dependency relationship may not be as clear.

## Stopping Watchers

In most cases, we do not need to manually stop watchers. However, if you do need to manually stop a watcher, you can call **the function returned** by `watch` or `watch_effect`:

```python:no-line-numbers
unwatch = watch_effect(lambda: None)

# ... when the watcher is no longer needed
unwatch()
```
