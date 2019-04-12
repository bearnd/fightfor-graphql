# coding=utf-8

import operator

import graphene
from graphene.utils.str_converters import to_camel_case
from graphene_sqlalchemy.registry import get_global_registry
from graphene_sqlalchemy.types import construct_fields


def create_class(name, argnames, base=graphene.InputObjectType):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # here, the argnames variable is the one passed to the
            # ClassFactory call
            if key not in argnames:
                msg = "Argument {} not valid for {}"
                msg_fmt = msg.format(key, self.__class__.__name__)
                raise TypeError(msg_fmt)
            setattr(self, key, value)
        base.__init__(self, name[:-len("Class")])
    newclass = type(name, (base,), {"__init__": __init__})
    return newclass


class FilterOperatorType(graphene.Enum):

    EQ = operator.eq
    NE = operator.ne
    GT = operator.gt
    LT = operator.lt
    LE = operator.le
    GE = operator.ge


def create_filter_class(name, field_name, value_type):
    def __init__(self, **kwargs):
        graphene.AbstractType.__init__(self)
    newclass = type(name, (graphene.AbstractType,), {"__init__": __init__})
    newclass._field = field_name
    newclass.value = value_type
    return newclass


def create_orm_filter_classes(orm_class):

    fields = construct_fields(orm_class, get_global_registry(), [], [])

    filter_classes = []
    for field_name, field in fields.items():
        name = "{}Filter{}".format(
            orm_class.__name__,
            to_camel_case(field_name).capitalize()
        )
        filter_class = create_filter_class(
            name=name,
            field_name=field_name,
            value_type=field.get_type()
        )
        filter_classes.append(filter_class)

    return filter_classes
