# coding=utf-8

from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_mt import Descriptor as ModelDescriptor
from fform.orm_mt import TreeNumber as ModelTreeNumber
from fform.orm_mt import DescriptorSynonym as ModelDescriptorSynonym


class TypeDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptor


class TypeTreeNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelTreeNumber
