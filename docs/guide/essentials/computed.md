---
prev: ./reactivity-fundamentals
next: ./watchers
---

# Computed Properties

**Contents**

[[toc]]

## Basic Example

`computed()` creates a read-only ref object based on a function, and its value is the return value of the function. This ref object is called a **computed property**. If the function contains reactive objects that participate in the computation, the computed property will automatically update when these reactive objects change.

For example, we have a reactive dictionary containing nested arrays: 

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

We want to display different information stored in the `message` variable based on whether the author has some books or not. Without using computed properties, we would need to manually update the value of `message` every time we modify `author['books']`, which is quite cumbersome:

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

Therefore, we recommend using **computed properties** to describe complex logic that depends on reactive state, this is the example after refactoring:

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

# a computed property ref
message = computed(update_message)
print(message.value)  # Zhang San, you have 2 books.

author['books'].pop()
print(message.value)  # Zhang San, you have 1 books.

author['books'].pop()
print(message.value)  # Zhang San, you have no books.
```

Here we define a `computed property` message. The `computed()` function expects a getter function as a parameter, which returns a **computed property ref**. Like a regular ref, you can access the computed result through `message.value`.

PyReactivity's computed properties automatically track reactive dependencies. It detects that `message` depends on `author['books']`, so when `author['books']` changes, `message` will automatically update as well.

Similarly, if other reactive variables depend on `message`, they will also automatically update when `message` is updated.

## Caching of Computed Properties

You may notice that calling the `update_message()` function directly gets the same result as `message.value`, so why use computed properties?

This is because the `update_message()` function does not **cache the result**, it recalculates every time it is called. While computed properties automatically cache results and only recalculate when their reactive dependencies are updated. This means that as long as `author['books']` does not change, accessing `message` multiple times will immediately return the previous computation result without having to execute the `update_message()` function again.

Why caching is needed? Imagine we have a very performance-intensive computed property `foo` that needs to loop through a huge list and do many computation logic and possibly other computed properties depend on `foo`. Without caching, we would be executing the getter function of `foo` multiple times, which is actually unnecessary! If you are sure caching is not needed, you can also use method calls.

## Note

### Getter Function Should not Have Side Effects

The getter function of computed properties should only do the calculation and not have any other side effects, this is very important, please remember not to modify values outside the getter function!

A computed property declaration describes how to derive a value from other values. Therefore, the getter's job should be limited to calculating and returning this value. In later guides, we will discuss how to use listeners to run code that causes side effects based on changes in other reactive states.

### Cannot Directly Modify Computed Property Value

The value returned from a computed property is **derived state**. It can be thought of as a "temporary snapshot" that is created each time the source state changes.

Modifying the snapshot is meaningless, so the returned value of the computed property is read-only and should never be changed - the source state on which it depends should be updated to trigger a new calculation.
