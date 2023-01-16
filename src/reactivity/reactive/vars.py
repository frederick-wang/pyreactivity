from typing import cast

immutable_builtin_types = (
    int,
    float,
    complex,
    str,
    bool,
    cast(type, frozenset),
    bytes,
)

immutable_but_containable_builtin_types = (cast(type, tuple),)

mutable_builtin_types = (
    cast(type, list),
    bytearray,
    memoryview,
    cast(type, set),
    cast(type, dict),
)

supported_builtin_types = (
    *immutable_builtin_types,
    *immutable_but_containable_builtin_types,
    *mutable_builtin_types,
)
