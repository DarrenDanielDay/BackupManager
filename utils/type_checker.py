from typing import *
import typing


def strong_check(value, expected_type: Union[Type, Tuple[Type, ...]]):
    if isinstance(expected_type, tuple):
        return any(strong_check(value, item) for item in expected_type)
    return type(value) is expected_type

def weak_check(value, expected_type):
    return isinstance(value, expected_type)

def general_check(value, expected_type, checker = weak_check):
    if isinstance(expected_type, typing._GenericAlias):
        origin = expected_type.__origin__
        if origin is typing.Union:
            return isinstance(value, expected_type.__args__)
        elif origin is list or origin is tuple:
            return checker(value, origin) and all(checker(item, expected_type.__args__) for item in value)
        elif origin is dict:
            kt, vt = expected_type.__args__
            return checker(value, origin) and all(checker(k, kt) and checker(v, vt) for k, v in value.items())
        else:
            print(f'cannot check type {origin}, assuming it is right.')
            return True
    else:
        return checker(value, expected_type)


