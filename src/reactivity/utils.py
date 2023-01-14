from reactivity.flags import FLAG_OF_READONLY


def is_readonly(obj: object) -> bool:
    return hasattr(obj, FLAG_OF_READONLY)
