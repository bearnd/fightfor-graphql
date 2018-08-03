# coding=utf-8

from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_mt import Descriptor as ModelDescriptor
from fform.orm_mt import TreeNumber as ModelTreeNumber
from fform.orm_mt import DescriptorSynonym as ModelDescriptorSynonym
from fform.orm_mt import Concept as ModelConcept
from fform.orm_mt import Qualifier as ModelQualifier


class TypeDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptor


class TypeTreeNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelTreeNumber


class TypeDescriptorSynonym(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorSynonym


class TypeConcept(SQLAlchemyObjectType):
    class Meta:
        model = ModelConcept


class TypeQualifier(SQLAlchemyObjectType):
    class Meta:
        model = ModelQualifier
