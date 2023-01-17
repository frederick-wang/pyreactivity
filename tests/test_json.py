import io
import json

from reactivity import reactive, ref


# should be able to json.dumps (reactive)
def test_reactive_json_dumps_reactive():
    obj = reactive({'foo': {'bar': [1, 2, 3]}, 'baz': 1, 'a': 'Hello', 'b': True})
    assert json.dumps(obj) == '{"foo": {"bar": [1, 2, 3]}, "baz": 1, "a": "Hello", "b": true}'
    f = io.StringIO()
    json.dump(obj, f)
    assert f.getvalue() == '{"foo": {"bar": [1, 2, 3]}, "baz": 1, "a": "Hello", "b": true}'


# should be able to json.dumps (ref.value)
def test_reactive_json_dumps_ref_value():
    obj = ref({'foo': {'bar': [1, 2, 3]}, 'baz': 1, 'a': 'Hello', 'b': True})
    assert json.dumps(obj.value) == '{"foo": {"bar": [1, 2, 3]}, "baz": 1, "a": "Hello", "b": true}'
    f = io.StringIO()
    json.dump(obj.value, f)
    assert f.getvalue() == '{"foo": {"bar": [1, 2, 3]}, "baz": 1, "a": "Hello", "b": true}'


# should be able to json.dumps (ref)
def test_reactive_json_dumps_ref():
    obj = ref({'foo': ref({'bar': [1, 2, 3]}), 'baz': ref(1), 'a': 'Hello', 'b': True})
    assert json.dumps(obj) == '{"foo": {"bar": [1, 2, 3]}, "baz": 1, "a": "Hello", "b": true}'
    f = io.StringIO()
    json.dump(obj, f)
    assert f.getvalue() == '{"foo": {"bar": [1, 2, 3]}, "baz": 1, "a": "Hello", "b": true}'


# should be able to json.dumps (ref) when using custom encoder
def test_reactive_json_dumps_ref_custom_encoder():

    class ComplexEncoder(json.JSONEncoder):

        def default(self, obj):
            if isinstance(obj, complex):
                return [obj.real, obj.imag]
            return json.JSONEncoder.default(self, obj)

    obj = ref({'foo': ref({'bar': [ref(1), 2, 3]}), 'baz': ref(1 + 1j), 'c': 2 + 1j})
    assert json.dumps(obj, cls=ComplexEncoder) == '{"foo": {"bar": [1, 2, 3]}, "baz": [1.0, 1.0], "c": [2.0, 1.0]}'
    f = io.StringIO()
    json.dump(obj, f, cls=ComplexEncoder)
    assert f.getvalue() == '{"foo": {"bar": [1, 2, 3]}, "baz": [1.0, 1.0], "c": [2.0, 1.0]}'


# should be able to jsom.dumps (ref) when set default parameter
def test_reactive_json_dumps_ref_default_parameter():

    def complex_handler(obj):
        if isinstance(obj, complex):
            return [obj.real, obj.imag]
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    obj = ref({'foo': ref({'bar': [ref(1), 2, 3]}), 'baz': ref(1 + 1j), 'c': 2 + 1j})
    assert json.dumps(obj, default=complex_handler) == '{"foo": {"bar": [1, 2, 3]}, "baz": [1.0, 1.0], "c": [2.0, 1.0]}'
    f = io.StringIO()
    json.dump(obj, f, default=complex_handler)
    assert f.getvalue() == '{"foo": {"bar": [1, 2, 3]}, "baz": [1.0, 1.0], "c": [2.0, 1.0]}'


# should be able to json.dumps int wrapped in ref
def test_reactive_json_dumps_ref_int():
    obj = ref(1)
    assert json.dumps(obj) == '1'


# should be able to json.dumps str wrapped in ref
def test_reactive_json_dumps_ref_str():
    obj = ref('Hello')
    assert json.dumps(obj) == '"Hello"'
    f = io.StringIO()
    json.dump(obj, f)
    assert f.getvalue() == '"Hello"'


# should be able to json.dumps bool wrapped in ref
def test_reactive_json_dumps_ref_bool():
    obj = ref(True)
    assert json.dumps(obj) == 'true'
    f = io.StringIO()
    json.dump(obj, f)
    assert f.getvalue() == 'true'


# should be able to json.dumps None wrapped in ref
def test_reactive_json_dumps_ref_none():
    obj = ref(None)
    assert json.dumps(obj) == 'null'
    f = io.StringIO()
    json.dump(obj, f)
    assert f.getvalue() == 'null'
