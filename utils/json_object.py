from typing import *
from abc import abstractmethod
import json
from enum import Enum
import typing
import pathlib

from utils.singletone import Singletone
from utils.type_checker import general_check

T = TypeVar("T")


class JSONConverter:
    @abstractmethod
    def to_json(self, value): ...

    @abstractmethod
    def from_json(self, value): ...


class _Echo(JSONConverter, Singletone):
    def to_json(self, value): return value

    def from_json(self, value): return value


class ForceStringCastConverter(JSONConverter):
    def __init__(self, constructor: Type[Any]
                 ): self.__constructor = constructor

    def from_json(self, value): return self.__constructor(value)

    def to_json(self, value): return str(value)


class ListJSONConverter(JSONConverter):
    def __init__(self, item_converter: JSONConverter):
        self.__converter = item_converter

    def to_json(self, value: List[Any]):
        return [self.__converter.to_json(item) for item in value]

    def from_json(self, value: List[Any]):
        return [self.__converter.from_json(item) for item in value]


class DictJSONConverter(JSONConverter):
    def __init__(self, item_converter: JSONConverter):
        self.__converter = item_converter

    def to_json(self, value: Dict[str, Any]):
        return {k: self.__converter.to_json(v) for k, v in value.items()}

    def from_json(self, value: Dict[str, Any]):
        return {k: self.__converter.from_json(v) for k, v in value.items()}


class NullableJSONConverter(JSONConverter):
    def __init__(self, item_converter: JSONConverter):
        self.__converter = item_converter

    def to_json(self, value: Optional[Any]):
        return self.__converter.to_json(value) if value is not None else None

    def from_json(self, value: Optional[Any]):
        return self.__converter.from_json(value) if value is not None else None


class SimpleJSONConverter(JSONConverter):
    def __init__(self, json_type: "Type[JSONObject]" = None):
        """
        if `json_type` is not given, the converter will use builtin-function `type`
        to determine the json object's type.
        """
        self.__type = json_type

    def to_json(self, value: "JSONObject") -> Dict[str, Any]:
        json_dict = {}
        json_type = self.__type if self.__type is not None else type(value)
        for item in json_type.__dict__.values():
            if isinstance(item, JSONItem):
                json_dict[item.json_key] = item.convert_to_json(
                    value, json_type)
        return json_dict

    def from_json(self, json_dict: Dict[str, Any]) -> "JSONObject":
        json_type = self.__type if self.__type is not None else type(value)
        instance = json_type()
        try:
            for item in json_type.__dict__.values():
                if isinstance(item, JSONItem):
                    value = json_dict[item.json_key]
                    item.load_from_json(instance, value)
        except KeyError as ke:
            raise ValueError(
                f"Missing key {repr(ke.args[0])} in JSON string.") from ke
        except BaseException as e:
            raise ValueError(f"Failed to convert: {e}") from e
        return instance


class BasicTypesConverter(Singletone):
    def __init__(self):
        if not hasattr(self, 'converters'):
            self.converters: Dict[Type, JSONConverter] = {}

    def register_converter(self, object_type: Type[T], converter: JSONConverter) -> JSONConverter:
        if object_type in self.converters.keys():
            raise ValueError(
                f"type {object_type} 's  converter has been already registered.")
        self.converters[object_type] = converter
        return converter

    def get_converter(self, object_type: Union[Type, typing._GenericAlias]) -> JSONConverter:
        if object_type not in self.converters.keys():
            if isinstance(object_type, typing._GenericAlias):
                object_type: typing._GenericAlias
                type_args = object_type.__args__
                origin = object_type.__origin__
                if origin is list:
                    return ListJSONConverter(self.get_converter(type_args[0]))
                elif origin is dict:
                    kt, vt = type_args
                    if kt is not str:
                        raise ValueError(
                            f"Dict keys in json must be str, not {kt}")
                    else:
                        return self.register_converter(object_type, DictJSONConverter(self.get_converter(vt)))
                elif origin is typing.Union and len(type_args) == 2 and any(item is type(None) for item in type_args):
                    not_none_type = next(
                        filter(lambda t: t is not type(None), type_args))
                    return self.register_converter(object_type, NullableJSONConverter(self.get_converter(not_none_type)))
            else:
                if issubclass(object_type, Enum):
                    return self.register_converter(object_type, EnumConverter(object_type))
                elif issubclass(object_type, JSONObject):
                    return self.register_converter(object_type, SimpleJSONConverter(object_type))
                elif issubclass(object_type, pathlib.Path):
                    return self.register_converter(object_type, ForceStringCastConverter(object_type))
                else:
                    print('warning: no converter found')
                    return _Echo()
        return self.converters[object_type]


for simple_type in [int, str, float, bool]:
    BasicTypesConverter().register_converter(simple_type, _Echo())


class EnumConverter(JSONConverter):
    def __init__(self, enum_type: Type[Enum]):
        self.__enum_type = enum_type

    def from_json(self, value):
        return self.__enum_type[
            next(
                filter(
                    lambda key: self.__enum_type[key].value == value,
                    self.__enum_type.__members__.keys()
                )
            )
        ]

    def to_json(self, value: Type[Enum]):
        return value.value


class JSONItem:
    @staticmethod
    def __generate_name(key: str):
        ls = []
        word = []
        for c in key:
            if c.isupper():
                ls.append(''.join(word))
                word.clear()
            word.append(c.lower())

        return f'___{"_".join(ls)}'

    def __init__(self, json_key: str, default: Any, attribute_name: str = None, expected_type: Type = None, converter: JSONConverter = None):
        if expected_type is not None:
            if not general_check(default, expected_type):
                raise ValueError(
                    f"default value {default} of JSONItem is not valid instance of {expected_type}")
        else:
            if default is None:
                raise ValueError(
                    "if you want to make default value to be 'None' or null, you should give the 'expected_type' paramter as Optional[...]")
            expected_type = type(default)
        self.__key = json_key
        self.__name = attribute_name if attribute_name is not None else JSONItem.__generate_name(
            json_key)
        self.__default = default
        self.__converter = converter if converter is not None else BasicTypesConverter(
        ).get_converter(expected_type)
        self.__expected_type = expected_type

    @property
    def json_key(self) -> str:
        return self.__key

    @property
    def expected_type(self) -> Type:
        return self.__expected_type

    def __get__(self, instance, cls):
        return getattr(instance, self.__name, self.__default)

    def convert_to_json(self, instance, cls):
        return self.__converter.to_json(self.__get__(instance, cls))

    def __set__(self, instance, value):
        if not general_check(value, self.__expected_type):
            raise ValueError(
                f"cannot set value of type {type(value)} to JSONItem of type {self.__expected_type}")
        setattr(instance, self.__name, value)

    def load_from_json(self, instance, value):
        self.__set__(instance, self.__converter.from_json(value))


class JSONObject:
    @classmethod
    def load_from_dict(cls, json_dict: Dict[str, Any]) -> "JSONObject":
        return SimpleJSONConverter(cls).from_json(json_dict)

    @classmethod
    def to_json_dict(cls, instance: "JSONObject") -> Dict[str, Any]:
        return SimpleJSONConverter(cls).to_json(instance)


def demo():
    class A(JSONObject):
        a_prop = JSONItem('aProp', [])
        b_prop = JSONItem('bProp', "b prop dft")

    class B(JSONObject):
        c_prop = JSONItem('cProp', "c prop dft")
        d_prop = JSONItem('dProp', "ddd", converter=SimpleJSONConverter(A))

    b = B()
    b.c_prop = "changed cProp's value"
    print(json.dumps(b.to_json_dict(b), sort_keys=True, indent=4))


if __name__ == "__main__":
    demo()
