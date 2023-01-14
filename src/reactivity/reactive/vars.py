immutable_builtin_types = (
    int,
    float,
    str,
    bool,
    frozenset,
    bytes,
)

immutable_but_containable_builtin_types = (tuple,)

mutable_builtin_types = (
    list,
    bytearray,
    memoryview,
    set,
    dict,
)

supported_builtin_types = (
    *immutable_builtin_types,
    *immutable_but_containable_builtin_types,
    *mutable_builtin_types,
)
