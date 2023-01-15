import pytest
from reactivity import watch, watch_effect, reactive, ref, computed


# effect
def test_effect():
    state = reactive({'count': 0})
    dummy = None

    def func():
        nonlocal dummy
        dummy = state['count']

    watch_effect(func)
    assert dummy == 0

    state['count'] += 1
    assert dummy == 1


# watching single source: getter
def test_watching_single_source_getter():
    state = reactive({'count': 0})
    dummy = None

    def cb(count, prev_count):
        nonlocal dummy
        dummy = (count, prev_count)
        # assert types
        assert isinstance(count, int)
        if prev_count is not None:
            assert isinstance(prev_count, int)

    watch(lambda: state['count'], cb)
    state['count'] += 1
    assert dummy == (1, 0)


# watching single source: ref
def test_watching_single_source_ref():
    count = ref(0)
    dummy = None

    def func(count, prev_count):
        nonlocal dummy
        dummy = (count, prev_count)
        # assert types
        assert type(count) == int
        if prev_count is not None:
            assert type(prev_count) == int

    watch(count, func)
    count.value += 1
    assert dummy == (1, 0)


# watching single source: array
def test_watching_single_source_array():
    array: 'list[int]' = reactive([])
    spy_calls = 0

    def spy(new_value):
        nonlocal spy_calls
        spy_calls += 1
        assert new_value == [1]

    watch(array, spy)
    array.append(1)
    assert array == [1]
    assert spy_calls == 1


# should not fire if watched getter result did not change
def test_not_fire_if_watched_getter_result_did_not_change():
    spy_calls = 0

    def spy():
        nonlocal spy_calls
        spy_calls += 1

    n = ref(0)
    watch(lambda: n.value % 2, spy)
    n.value += 1
    assert spy_calls == 1

    n.value += 2
    # should not be called again because getter result did not change
    assert spy_calls == 1


# watching single source: computed ref
def test_watching_single_source_computed_ref():
    count = ref(0)
    plus = computed(lambda: count.value + 1)
    dummy = None

    def func(count, prev_count):
        nonlocal dummy
        dummy = (count, prev_count)
        # assert types
        assert type(count) == int
        if prev_count is not None:
            assert type(prev_count) == int

    watch(plus, func)
    count.value += 1
    assert dummy == (2, 1)


# watching primitive with deep: true
def test_watching_primitive_with_deep_true():
    count = ref(0)
    dummy = None

    def func(c, prev_count):
        nonlocal dummy
        dummy = (c, prev_count)

    watch(count, func, deep=True)
    count.value += 1
    assert dummy == (1, 0)


# directly watching reactive object (with automatic deep: true)
def test_directly_watching_reactive_object_with_automatic_deep_true():
    src = reactive({'count': 0})
    dummy = None

    def func(v):
        nonlocal dummy
        dummy = v['count']

    watch(src, func)
    src['count'] += 1
    assert dummy == 1


# watching multiple sources
def test_watching_multiple_sources():
    state = reactive({'count': 1})
    count = ref(1)
    plus = computed(lambda: count.value + 1)

    dummy = None

    def cb(vals, old_vals):
        nonlocal dummy
        dummy = (vals, old_vals)
        # assert types
        assert type(vals) == list
        assert type(old_vals) == list

    watch([lambda: state['count'], count, plus], cb)

    state['count'] += 1
    assert dummy == ([2, 1, 2], [1, 1, 2])
    count.value += 1
    assert dummy == ([2, 2, 3], [2, 1, 2])


# watching multiple sources: undefined initial values and immediate: true
def test_watching_multiple_sources_undefined_initial_values_and_immediate_true():
    a = ref()
    b = ref()
    called = False

    def cb(vals, prev_vals):
        nonlocal called
        called = True
        assert vals == [None, None]
        assert prev_vals == [None, None]

    watch([a, b], cb, immediate=True)
    assert called


# watching multiple sources: readonly array
def test_watching_multiple_sources_readonly_array():
    state = reactive({'count': 1})
    status = ref(False)

    dummy = None

    def cb(vals, old_vals):
        nonlocal dummy
        dummy = (vals, old_vals)
        count, _ = vals
        _, old_status = old_vals
        # assert types
        assert type(count) == int
        assert type(old_status) == bool

    watch([lambda: state['count'], status], cb)
    state['count'] += 1
    assert dummy == ([2, False], [1, False])
    status.value = True
    assert dummy == ([2, True], [2, False])


# watching multiple sources: reactive object (with automatic deep: true)
def test_watching_multiple_sources_reactive_object_with_automatic_deep_true():
    src = reactive({'count': 0})
    dummy = None

    def cb(vals):
        nonlocal dummy
        state = vals[0]
        dummy = state
        # assert types
        assert state['count'] == 1

    watch([src], cb)
    src['count'] += 1
    assert dummy == {'count': 1}


# warn invalid watch source
def test_warn_invalid_watch_source():
    with pytest.raises(TypeError, match='Invalid watch source type'):
        watch(1, lambda: None)


# warn invalid watch source: multiple sources
def test_warn_invalid_watch_source_multiple_sources():
    with pytest.raises(TypeError, match='Invalid watch source type'):
        watch([1], lambda: None)


# stopping the watcher (effect)
def test_stopping_the_watcher_effect():
    state = reactive({'count': 0})
    dummy = None

    def e():
        nonlocal dummy
        dummy = state['count']

    stop = watch_effect(e)
    assert dummy == 0

    stop()
    state['count'] += 1
    assert dummy == 0


# stopping the watcher (with source)
def test_stopping_the_watcher_with_source():
    state = reactive({'count': 0})
    dummy = None

    def cb(count):
        nonlocal dummy
        dummy = count

    stop = watch(lambda: state['count'], cb)

    state['count'] += 1
    assert dummy == 1

    stop()
    state['count'] += 1
    # should not update
    assert dummy == 1


# cleanup registration (effect)
def test_cleanup_registration_effect():
    state = reactive({'count': 0})
    cleanup_calls = 0

    def cleanup():
        nonlocal cleanup_calls
        cleanup_calls += 1

    dummy = None

    def e(on_cleanup):
        nonlocal dummy
        on_cleanup(cleanup)
        dummy = state['count']

    stop = watch_effect(e)
    assert dummy == 0

    state['count'] += 1
    assert cleanup_calls == 1
    assert dummy == 1

    stop()
    assert cleanup_calls == 2


# cleanup registration (with source)
def test_cleanup_registration_with_source():
    count = ref(0)
    cleanup_calls = 0

    def cleanup():
        nonlocal cleanup_calls
        cleanup_calls += 1

    dummy = None

    def cb(count, prev_count, on_cleanup):
        nonlocal dummy
        on_cleanup(cleanup)
        dummy = count

    stop = watch(count, cb)

    count.value += 1
    assert cleanup_calls == 0
    assert dummy == 1

    count.value += 1
    assert cleanup_calls == 1
    assert dummy == 2

    stop()
    assert cleanup_calls == 2


# deep
def test_deep():
    state = reactive({
        'nested': {
            'count': ref(0)
        },
        'array': [1, 2, 3],
        'map': dict([('a', 1), ('b', 2)]),
        'set': {1, 2, 3},
    })

    dummy = None

    def cb(state):
        nonlocal dummy
        dummy = [
            state['nested']['count'],
            state['array'][0],
            state['map'].get('a'),
            1 in state['set'],
        ]

    watch(lambda: state, cb, deep=True)

    state['nested']['count'] += 1
    assert dummy == [1, 1, 1, True]

    # nested array mutation
    state['array'][0] = 2
    assert dummy == [1, 2, 1, True]

    # nested map mutation
    state['map']['a'] = 2
    assert dummy == [1, 2, 2, True]

    # nested set mutation
    state['set'].remove(1)
    assert dummy == [1, 2, 2, False]


# watching deep ref
def test_watching_deep_ref():
    count = ref(0)
    double = computed(lambda: count.value * 2)
    state = reactive([count, double])

    dummy = None

    def cb(state):
        nonlocal dummy
        dummy = [state[0].value, state[1].value]

    watch(lambda: state, cb, deep=True)

    count.value += 1
    assert dummy == [1, 2]


# immediate
def test_immediate():
    count = ref(0)
    cb_calls = 0

    def cb():
        nonlocal cb_calls
        cb_calls += 1

    watch(count, cb, immediate=True)
    assert cb_calls == 1
    count.value += 1
    assert cb_calls == 2


# immediate: triggers when initial value is null
def test_immediate_triggers_when_initial_value_is_null():
    state = ref(None)
    spy_called = False

    def spy():
        nonlocal spy_called
        spy_called = True

    watch(lambda: state.value, spy, immediate=True)
    assert spy_called


# immediate: triggers when initial value is undefined
def test_immediate_triggers_when_initial_value_is_undefined():
    state = ref()
    spy_calls = 0

    def spy():
        nonlocal spy_calls
        spy_calls += 1

    watch(lambda: state.value, spy, immediate=True)
    state.value = 3
    assert spy_calls == 2
    # testing if None can trigger the watcher
    state.value = None
    assert spy_calls == 3
    # it shouldn't trigger if the same value is set
    state.value = None
    assert spy_calls == 3


# warn immediate option when using effect
def test_warn_immediate_option_when_using_effect():
    count = ref(0)
    dummy = None

    def e():
        nonlocal dummy
        dummy = count.value

    with pytest.raises(TypeError, match='Unknown keyword argument immediate for watch_effect().'):
        watch_effect(e, immediate=True)  # type: ignore


# warn and not respect deep option when using effect
def test_warn_and_not_respect_deep_option_when_using_effect():
    arr = ref([1, [2]])
    spy_calls = 0

    def spy():
        nonlocal spy_calls
        spy_calls += 1

    def e():
        spy()
        return arr

    with pytest.raises(TypeError, match='Unknown keyword argument deep for watch_effect().'):
        watch_effect(e, deep=True)  # type: ignore


# watching sources: ref<any[]>
def test_watching_sources_ref_any():
    foo = ref([1])
    spy_calls = 0

    def spy():
        nonlocal spy_calls
        spy_calls += 1

    def cb():
        spy()

    watch(foo, cb)
    foo.value = [*foo.value, *foo.value]
    assert spy_calls == 1
    assert foo.value == [1, 1]


# watching multiple sources: computed
def test_watching_multiple_sources_computed():
    count = 0
    value = ref('1')
    plus = computed(lambda: not not value.value)

    def cb():
        nonlocal count
        count += 1

    watch([plus], cb)
    value.value = '2'
    assert plus.value == True
    assert count == 0
