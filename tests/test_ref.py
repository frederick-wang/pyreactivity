from reactivity import computed, is_ref, reactive, ref, effect, unref


# should hold a value
def test_hold_value():
    a = ref(1)
    assert a.value == 1
    a.value = 2
    assert a.value == 2


# should be reactive
def test_be_reactive():
    a = ref(1)
    dummy = None
    calls = 0

    def func():
        nonlocal dummy, calls
        calls += 1
        dummy = a.value

    effect(func)

    assert calls == 1
    assert dummy == 1
    a.value = 2
    assert calls == 2
    assert dummy == 2
    a.value = 2
    assert calls == 2


# should make nested properties reactive
def test_make_nested_properties_reactive():
    a = ref({'count': 1})
    dummy = None

    def func():
        nonlocal dummy
        dummy = a.value['count']

    effect(func)
    assert dummy == 1
    a.value['count'] = 2
    assert dummy == 2


# should work without initial value
def test_work_without_initial_value():
    a = ref()
    dummy = None

    def func():
        nonlocal dummy
        dummy = a.value

    effect(func)
    assert dummy is None
    a.value = 2
    assert dummy == 2


# should work like a normal property when nested in a reactive object
def test_work_like_a_normal_property_when_nested_in_a_reactive_object():
    a = ref(1)
    obj = reactive({
        'a': a,
        'b': {
            'c': a
        },
    })
    dummy1 = None
    dummy2 = None

    def func():
        nonlocal dummy1, dummy2
        dummy1 = obj['a']
        dummy2 = obj['b']['c']

    effect(func)

    def assert_dummies_equal_to(val: int):
        assert dummy1 == val
        assert dummy2 == val

    assert_dummies_equal_to(1)
    a.value += 1
    assert_dummies_equal_to(2)
    # obj['a'] += 1
    # assert_dummies_equal_to(3)
    # obj['b']['c'] += 1
    # assert_dummies_equal_to(4)


# should unwrap nested ref in types
def test_unwrap_nested_ref_in_types():
    a = ref(0)
    b = ref(a)

    assert type(b.value + 1) == int


# should unwrap nested values in types
def test_unwrap_nested_values_in_types():
    a = {
        'b': ref(0),
    }
    c = ref(a)

    assert type(c.value['b'] + 1) == int  # type: ignore


# should NOT unwrap ref types nested inside lists
def test_not_unwrap_ref_types_nested_inside_lists():
    arr = ref([1, ref(3)]).value
    assert is_ref(arr[0]) == False
    assert is_ref(arr[1]) == True
    assert arr[1].value == 3  # type: ignore


# should keep tuple types
def test_keep_tuple_types():
    t = [
        0,
        '1',
        {
            'a': 1
        },
        lambda: 0,
        ref(0),
    ]
    t_ref = ref(t)

    t_ref.value[0] += 1
    assert t_ref.value[0] == 1
    t_ref.value[1] += '1'
    assert t_ref.value[1] == '11'
    t_ref.value[2]['a'] += 1
    assert t_ref.value[2]['a'] == 2
    assert t_ref.value[3]() == 0
    t_ref.value[4].value += 1
    assert t_ref.value[4].value == 1


# unref
def test_unref():
    assert unref(1) == 1
    assert unref(ref(1)) == 1


# isRef
def test_is_ref():
    assert is_ref(ref(1)) == True
    assert is_ref(computed(lambda: 1)) == True

    assert is_ref(0) == False
    assert is_ref(1) == False

    # an object that looks like a ref isn't necessarily a ref
    class Obj:
        value = 0

    assert is_ref(Obj()) == False


# should not trigger when setting value to same proxy
def test_not_trigger_when_setting_value_to_same_proxy():
    obj = reactive({'count': 0})

    a = ref(obj)
    spy1_calls = 0

    def spy1():
        nonlocal spy1_calls
        spy1_calls += 1
        return a.value

    effect(spy1)

    a.value = obj
    assert spy1_calls == 1
