# pyreactivity

A Python package for reactivity like Vue.js.

Test cases for all currently supported features are in `tests` directory, written in pytest. To run tests, use `pytest` command.

## Installation

```bash
pip install pyreactivity
```

## Supported features

- [x] `ref` function
- [x] `computed` function
- [x] `reactive` function
- [x] `effect` function
- [x] `watch` function
- [x] `watch_effect` ( `watchEffect` ) function
- [x] `is_ref` ( `isRef` ) function
- [x] `is_computed_ref` ( `isComputedRef` ) function
- [x] `unref` function
- [x] `is_reactive` ( `isReactive` ) function
- [x] `to_raw` ( `toRaw` ) function
- [x] `mark_raw` ( `markRaw` ) function

## Simple Demo

```python
from reactivity import ref, computed

a = ref('')
b = computed(lambda: ''.join(reversed(a.value)))
a.value = 'hello'
print(b.value)  # olleh
a.value = 'world'
print(b.value)  # dlrow
```

## Inspiration

This package is inspired by Vue.js.
