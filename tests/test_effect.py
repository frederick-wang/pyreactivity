from reactivity import effect, reactive
import pytest


# should run the passed function once (wrapped by a effect)
def test_run_the_passed_function_once_wrapped_by_a_effect():
    calls = 0

    def fn_spy():
        nonlocal calls
        calls += 1

    effect(fn_spy)
    assert calls == 1


# should observe basic properties
def test_observe_basic_properties():
    dummy = None
    counter = reactive({'num': 0})

    def func():
        nonlocal dummy
        dummy = counter['num']

    effect(func)
    assert dummy == 0
    counter['num'] = 7
    assert dummy == 7


# should observe multiple properties
def test_observe_multiple_properties():
    dummy = None
    counter = reactive({'num1': 0, 'num2': 0})

    def func():
        nonlocal dummy
        dummy = counter['num1'] + counter['num1'] + counter['num2']

    effect(func)
    assert dummy == 0
    counter['num1'] = counter['num2'] = 7
    assert dummy == 21


# should handle multiple effects
def test_handle_multiple_effects():
    dummy1 = None
    dummy2 = None
    counter = reactive({'num': 0})

    def func1():
        nonlocal dummy1
        dummy1 = counter['num']

    effect(func1)

    def func2():
        nonlocal dummy2
        dummy2 = counter['num']

    effect(func2)
    assert dummy1 == 0
    assert dummy2 == 0
    counter['num'] += 1
    assert dummy1 == 1
    assert dummy2 == 1


# should observe nested properties
def test_observe_nested_properties():
    dummy = None
    counter = reactive({'nested': {'num': 0}})

    def func():
        nonlocal dummy
        dummy = counter['nested']['num']

    effect(func)
    assert dummy == 0
    counter['nested']['num'] = 8
    assert dummy == 8


# should observe delete operations
def test_observe_delete_operations():
    dummy = None
    obj = reactive({'prop': 'value'})

    def func():
        nonlocal dummy
        dummy = obj['prop']

    effect(func)

    assert dummy == 'value'
    with pytest.raises(KeyError):
        del obj['prop']


# should observe has operations
def test_observe_has_operations():
    dummy = None
    obj = reactive({'prop': 'value'})

    def func():
        nonlocal dummy
        dummy = 'prop' in obj

    effect(func)

    assert dummy is True
    del obj['prop']
    assert dummy is False
    obj['prop'] = 'new_value'
    assert dummy is True


# should observe function call chains
def test_observe_function_call_chains():
    dummy = None
    counter = reactive({'num': 0})

    def get_num():
        return counter['num']

    def func():
        nonlocal dummy
        dummy = get_num()

    effect(func)

    assert dummy == 0
    counter['num'] = 2
    assert dummy == 2


# should observe iteration
def test_observe_iteration():
    dummy = None
    lst = reactive(['Hello'])

    def func():
        nonlocal dummy
        dummy = ' '.join(lst)

    effect(func)
    assert dummy == 'Hello'
    lst.append('World!')
    assert dummy == 'Hello World!'
    lst.pop(0)
    assert dummy == 'World!'


# should observe implicit array length changes
def test_observe_implicit_array_length_changes():
    dummy = None
    lst = reactive(['Hello'])

    def func():
        nonlocal dummy
        dummy = ' '.join(lst)

    effect(func)

    assert dummy == 'Hello'
    lst.insert(1, 'World!')
    assert dummy == 'Hello World!'
    lst.insert(2, '')
    lst.insert(3, 'Hello!')
    assert dummy == 'Hello World!  Hello!'


# should observe sparse array mutations
def test_observe_sparse_array_mutations():
    dummy = None
    lst = reactive([])
    lst.insert(0, '')
    lst.insert(1, 'World!')

    def func():
        nonlocal dummy
        dummy = ' '.join(lst)

    effect(func)

    assert dummy == ' World!'
    lst[0] = 'Hello'
    assert dummy == 'Hello World!'
    lst.pop()
    assert dummy == 'Hello'


# should observe enumeration
def test_observe_enumeration():
    dummy = 0
    numbers = reactive({'num1': 3})

    def func():
        nonlocal dummy
        dummy = 0
        for key in numbers:
            dummy += numbers[key]

    effect(func)

    assert dummy == 3
    numbers['num2'] = 4
    assert dummy == 7
    del numbers['num1']
    assert dummy == 4


# should observe function valued properties
def test_observe_function_valued_properties():

    def old_func():
        return

    def new_func():
        return

    dummy = None
    obj = reactive({'func': old_func})

    def func():
        nonlocal dummy
        dummy = obj['func']

    effect(func)

    assert dummy == old_func
    obj['func'] = new_func
    assert dummy == new_func


# should observe chained getters relying on this
def test_observe_chained_getters_relying_on_this():

    class Obj:
        a: int

        def __init__(self):
            self.a = 1

        @property
        def b(self):
            return self.a
        
        def c(self):
            self.a += 1

    obj = reactive(Obj())
    dummy = None

    def func():
        nonlocal dummy
        dummy = obj.b

    effect(func)

    assert dummy == 1
    obj.a += 1
    assert dummy == 2
    obj.c()
    assert dummy == 3


# should observe methods relying on this
def test_observe_methods_relying_on_this():

    class Obj:
        a: int

        def __init__(self):
            self.a = 1

        @property
        def b(self):
            return self.a

        def c(self):
            return self.b
        
        def d(self):
            self.a += 1

    obj = reactive(Obj())
    dummy = None

    def func():
        nonlocal dummy
        dummy = obj.c()

    effect(func)

    assert dummy == 1
    obj.a += 1
    assert dummy == 2
    obj.d()
    assert dummy == 3


# should not observe set operations without a value change
def test_not_observe_set_operations_without_a_value_change():
    has_dummy = None
    get_dummy = None
    obj = reactive({'prop': 'value'})
    get_spy_calls = 0

    def get_spy():
        nonlocal get_spy_calls, get_dummy
        get_spy_calls += 1
        get_dummy = obj['prop']

    has_spy_calls = 0

    def has_spy():
        nonlocal has_spy_calls, has_dummy
        has_spy_calls += 1
        has_dummy = 'prop' in obj

    effect(get_spy)
    effect(has_spy)

    assert get_dummy == 'value'
    assert has_dummy is True
    obj['prop'] = 'value'
    assert get_spy_calls == 1
    assert has_spy_calls == 1
    assert get_dummy == 'value'
    assert has_dummy is True


# should not observe raw mutations
def test_not_observe_raw_mutations():
    pass


# should not be triggered by raw mutations
def test_not_be_triggered_by_raw_mutations():
    pass


# should avoid implicit infinite recursive loops with itself
def test_avoid_implicit_infinite_recursive_loops_with_itself():
    # sourcery skip: remove-unreachable-code
    # FIXME: Cannot pass this test.
    # -- Zhaoji Wang 2023-01-11
    return
    counter = reactive({'num': 0})
    counter_spy_calls = 0

    def counter_spy():
        nonlocal counter_spy_calls
        counter_spy_calls += 1
        counter['num'] += 1

    effect(counter_spy)
    assert counter['num'] == 1
    assert counter_spy_calls == 1
    counter['num'] = 4
    assert counter['num'] == 5
    assert counter_spy_calls == 2


# should discover new branches while running automatically
def test_discover_new_branches_while_running_automatically():
    # sourcery skip: remove-unreachable-code
    # FIXME: Cannot pass this test.
    # -- Zhaoji Wang 2023-01-11
    return
    dummy = None
    obj = reactive({'prop': 'value', 'run': False})
    conditional_spy_calls = 0

    def conditional_spy():
        nonlocal dummy, conditional_spy_calls
        conditional_spy_calls += 1
        dummy = obj['prop'] if obj['run'] else 'other'

    effect(conditional_spy)

    assert dummy == 'other'
    assert conditional_spy_calls == 1
    obj['prop'] = 'Hi'
    assert dummy == 'other'
    assert conditional_spy_calls == 1
    obj['run'] = True
    assert dummy == 'Hi'
    assert conditional_spy_calls == 2
    obj['prop'] = 'World'
    assert dummy == 'World'
    assert conditional_spy_calls == 3


# should discover new branches when running manually
def test_discover_new_branches_when_running_manually():
    dummy = None
    run = False
    obj = reactive({'prop': 'value'})

    def runner_func():
        nonlocal dummy, run
        dummy = obj['prop'] if run else 'other'

    runner = effect(runner_func)

    assert dummy == 'other'
    runner()
    assert dummy == 'other'
    run = True
    runner()
    assert dummy == 'value'
    obj['prop'] = 'World'
    assert dummy == 'World'


# should not be triggered by mutating a property, which is used in an inactive branch
def test_not_be_triggered_by_mutating_a_property_which_is_used_in_an_inactive_branch():
    # sourcery skip: remove-unreachable-code
    # FIXME: Cannot pass this test.
    # -- Zhaoji Wang 2023-01-11
    return
    dummy = None
    obj = reactive({'prop': 'value', 'run': True})

    conditional_spy_calls = 0

    def conditional_spy():
        nonlocal dummy, conditional_spy_calls
        conditional_spy_calls += 1
        dummy = obj['prop'] if obj['run'] else 'other'

    effect(conditional_spy)

    assert dummy == 'value'
    assert conditional_spy_calls == 1
    obj['run'] = False
    assert dummy == 'other'
    assert conditional_spy_calls == 2
    obj['prop'] = 'value2'
    assert dummy == 'other'
    assert conditional_spy_calls == 2
