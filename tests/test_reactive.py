from reactivity import (computed, deep_to_raw, effect, is_reactive, is_ref, mark_raw, reactive, ref, to_raw)


# Dict
def test_dict():
    original = {'foo': 1}
    observed = reactive(original)
    assert observed is not original
    assert is_reactive(observed) == True
    assert is_reactive(original) == False
    # get
    assert observed['foo'] == 1
    # has
    assert 'foo' in observed
    # own keys
    assert list(observed.keys()) == ['foo']


# nested reactives
def test_nested_reactives():
    original = {
        'nested': {
            'foo': 1
        },
        'array': [{
            'bar': 2
        }],
    }
    observed = reactive(original)
    assert is_reactive(observed['nested']) == True
    assert is_reactive(observed['array']) == True
    assert is_reactive(observed['array'][0]) == True


# observing subtypes of IterableCollections(Dict, Set)
def test_observing_subtypes_of_IterableCollections():
    # subtypes of Dict

    class CustomDict(dict):
        pass

    cdict = reactive(CustomDict())

    assert isinstance(cdict, dict)
    assert is_reactive(cdict) == True
    cdict['key'] = {}
    assert is_reactive(cdict.get('key')) == True

    # subtypes of Set
    class CustomSet(set):
        pass

    cset = reactive(CustomSet())
    assert isinstance(cset, set)
    assert is_reactive(cset) == True

    dummy = None

    def func():
        nonlocal dummy
        dummy = 'value' in cset

    effect(func)
    assert dummy == False
    cset.add('value')
    assert dummy == True
    cset.remove('value')
    assert dummy == False


# observed value should proxy mutations to original (Dict)
def test_observed_value_should_proxy_mutations_to_original():
    original = {'foo': 1}
    observed = reactive(original)
    # set
    observed['bar'] = 1
    assert observed['bar'] == 1
    assert original['bar'] == 1
    # delete
    del observed['foo']
    assert 'foo' not in observed
    assert 'foo' not in original


# original value change should reflect in observed value (Object)
def test_original_value_change_should_reflect_in_observed_value():
    original = {'foo': 1}
    observed = reactive(original)
    # set
    original['bar'] = 1
    assert original['bar'] == 1
    assert observed['bar'] == 1
    # delete
    del original['foo']
    assert 'foo' not in original
    assert 'foo' not in observed


# setting a property with an unobserved value should wrap with reactive
def tset_a_property_with_an_unobserved_value_should_wrap_with_reactive():
    observed = reactive({'foo': None})
    raw = {}
    observed['foo'] = raw  # type: ignore
    assert observed['foo'] is not raw
    assert is_reactive(observed['foo']) == True


# observing already observed value should return same Proxy
def test_observing_already_observed_value_should_return_same_Proxy():
    original = {'foo': 1}
    observed = reactive(original)
    observed2 = reactive(observed)
    assert observed is observed2


# observing the same value multiple times should return same Proxy
def test_observing_the_same_value_multiple_times_should_return_same_Proxy():
    original = {'foo': 1}
    observed = reactive(original)
    observed2 = reactive(original)
    assert observed is observed2


# should not pollute original object with Proxies
def test_should_not_pollute_original_object_with_Proxies():
    original = {'foo': 1}
    original2 = {'bar': 2}
    observed = reactive(original)
    observed2 = reactive(original2)
    observed['bar'] = observed2  # type: ignore
    assert observed['bar'] is observed2
    assert original['bar'] is original2


# toRaw
def test_to_raw():
    original = {'foo': 1}
    observed = reactive(original)
    assert to_raw(observed) is original
    assert to_raw(original) is original
    a = {'foo': 1}
    b = {'bar': a}
    c = [b]
    observed = reactive(c)
    assert observed is not c
    assert observed[0] is not b
    assert observed[0]['bar'] is not a
    raw = to_raw(observed)
    assert raw is c
    assert raw[0] is b
    assert raw[0]['bar'] is a


# should not unwrap Ref<T>
def test_should_not_unwrap_RefT():
    observed_number_ref = reactive(ref(1))
    observed_dict_ref = reactive(ref({'foo': 1}))

    assert is_ref(observed_number_ref) == True
    assert is_ref(observed_dict_ref) == True


# should unwrap computed refs
def test_should_unwrap_computed_refs():
    a = computed(lambda: 1)
    b = computed(lambda: 1)
    obj = reactive({'a': a, 'b': b})
    assert type(obj['a']) == int
    assert type(obj['b']) == int


# should allow setting property from a ref to another ref
def test_should_allow_setting_property_from_a_ref_to_another_ref():
    foo = ref(0)
    bar = ref(1)
    observed = reactive({'a': foo})
    dummy = computed(lambda: observed['a'])
    assert dummy.value == 0

    observed['a'] = bar
    assert dummy.value == 1

    bar.value += 1
    assert dummy.value == 2


# should hold reactivity when a ref is as a member of a reactive object
def test_should_hold_reactivity_when_a_ref_is_as_a_member_of_a_reactive_object():
    count = ref(0)
    state = reactive({
        'count': count,
    })

    assert state['count'] == 0

    state['count'] = 1
    assert count.value == 1


# markRaw
def test_mark_raw():
    obj = reactive({
        'foo': {
            'a': 1
        },
        'bar': mark_raw({'b': 2}),
    })
    assert is_reactive(obj['foo']) == True
    assert is_reactive(obj['bar']) == False


# should not observe objects with __REACTIVE_SKIP__
def test_should_not_observe_objects_with__REACTIVE_SKIP__():

    class Original:
        foo: int
        __REACTIVE_SKIP__: bool

        def __init__(self):
            self.foo = 1
            self.__REACTIVE_SKIP__ = True

    original = Original()
    observed = reactive(original)
    assert is_reactive(observed) == False


# deep_to_raw
def test_deep_to_raw():
    a = {'foo': 1}
    b = [reactive(a)]
    assert b[0] is not a
    # The object returned by deep_to_raw is not guaranteed to be the original object.
    # It's only guaranteed to be a plain python object.
    assert 'reactive' not in str(type(deep_to_raw(b)[0]))


# compared with blank value
def test_compared_with_blank_value():
    # List
    assert reactive([]) != reactive([1, 2, 3])
    assert reactive([1, 2, 3]) != reactive([])

    # Dict
    assert reactive({}) != reactive({'foo': 1})
    assert reactive({'foo': 1}) != reactive({})

    # Set
    assert reactive(set()) != reactive({1, 2, 3})
    assert reactive({1, 2, 3}) != reactive(set())

    # Tuple
    assert reactive(tuple()) != reactive((1, 2, 3))
    assert reactive((1, 2, 3)) != reactive(tuple())

    # FrozenSet
    assert reactive(frozenset()) != reactive(frozenset({1, 2, 3}))
    assert reactive(frozenset({1, 2, 3})) != reactive(frozenset())
