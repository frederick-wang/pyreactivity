from reactivity.flags import FLAG_OF_COMPUTED_REF


def is_computed_ref(obj: object) -> bool:
    return hasattr(obj, FLAG_OF_COMPUTED_REF)
