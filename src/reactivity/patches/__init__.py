from .json_patch import patch_json, unpatch_json


def patch():
    patch_json()


def unpatch():
    unpatch_json()


__all__ = ['patch', 'patch_json', 'unpatch_json']
