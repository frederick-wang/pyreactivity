from reactivity import effect, reactive, computed
from reactivity.effect import ReactiveEffect


# should return updated value
def test_return_updated_value():
    value = reactive({'foo': 0})
    c_value = computed(lambda: value['foo'])

    assert c_value.value == 0
    value['foo'] = 1
    assert c_value.value == 1


# should compute lazily
def test_compute_lazily():
    value = reactive({'foo': 0})
    calls = 0

    def getter():
        nonlocal calls
        calls += 1
        return value['foo']

    c_value = computed(getter)

    # lazy
    assert calls == 0
    assert c_value.value == 0
    assert calls == 1

    # should not compute again
    c_value.value
    assert calls == 1

    # should not compute until needed
    value['foo'] = 1
    assert calls == 1

    # now it should compute
    assert c_value.value == 1
    assert calls == 2

    # should not compute again
    c_value.value
    assert calls == 2


# should trigger effect
def test_trigger_effect():
    value = reactive({'foo': 0})
    c_value = computed(lambda: value['foo'])
    dummy = None

    def func():
        nonlocal dummy
        dummy = c_value.value

    effect(func)
    assert dummy == 0
    value['foo'] = 1
    assert dummy == 1


# should work when chained
def test_work_when_chained():
    value = reactive({'foo': 0})
    c1 = computed(lambda: value['foo'])
    c2 = computed(lambda: c1.value + 1)
    assert c2.value == 1
    assert c1.value == 0
    value['foo'] += 1
    assert c2.value == 2
    assert c1.value == 1


# should trigger effect when chained
def test_trigger_effect_when_chained():
    value = reactive({'foo': 0})
    getter1_calls = 0
    getter2_calls = 0

    def getter1():
        nonlocal getter1_calls
        getter1_calls += 1
        return value['foo']

    def getter2():
        nonlocal getter2_calls
        getter2_calls += 1
        return c1.value + 1

    c1 = computed(getter1)
    c2 = computed(getter2)

    dummy = None

    def func():
        nonlocal dummy
        dummy = c2.value

    effect(func)

    assert dummy == 1
    assert getter1_calls == 1
    assert getter2_calls == 1
    value['foo'] += 1
    assert dummy == 2
    # should not result in duplicate calls
    assert getter1_calls == 2
    assert getter2_calls == 2


# should trigger effect when chained (mixed invocations)
def test_trigger_effect_when_chained_mixed_invocations():
    value = reactive({'foo': 0})
    getter1_calls = 0
    getter2_calls = 0

    def getter1():
        nonlocal getter1_calls
        getter1_calls += 1
        return value['foo']

    def getter2():
        nonlocal getter2_calls
        getter2_calls += 1
        return c1.value + 1

    c1 = computed(getter1)
    c2 = computed(getter2)

    dummy = None

    def func():
        nonlocal dummy
        dummy = c1.value + c2.value

    effect(func)

    assert dummy == 1
    assert getter1_calls == 1
    assert getter2_calls == 1
    value['foo'] += 1
    assert dummy == 3
    # should not result in duplicate calls
    assert getter1_calls == 2
    assert getter2_calls == 2


# should no longer update when stopped
def test_no_longer_update_when_stopped():
    value = reactive({'foo': 0})
    c_value = computed(lambda: value['foo'])
    dummy = None

    def func():
        nonlocal dummy
        dummy = c_value.value

    effect(func)

    assert dummy == 0
    value['foo'] = 1
    assert dummy == 1
    c_value_effect: ReactiveEffect = getattr(c_value, 'effect')
    c_value_effect.stop()
    value['foo'] = 2
    assert dummy == 1


# should expose value when stopped
def test_expose_value_when_stopped():
    x = computed(lambda: 1)
    x_effect: ReactiveEffect = getattr(x, 'effect')
    x_effect.stop()
    assert x.value == 1
