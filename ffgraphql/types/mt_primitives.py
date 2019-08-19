# coding=utf-8

from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_mt import Descriptor as ModelDescriptor
from fform.orm_mt import TreeNumber as ModelTreeNumber
from fform.orm_mt import DescriptorTreeNumber as ModelDescriptorTreeNumber
from fform.orm_mt import DescriptorSynonym as ModelDescriptorSynonym
from fform.orm_mt import Concept as ModelConcept
from fform.orm_mt import Qualifier as ModelQualifier
from fform.orm_mt import DescriptorDefinition as ModelDescriptorDefinition


class TypeDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptor
        exclude_fields = ["descriptor_class"]


class TypeTreeNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelTreeNumber


class TypeDescriptorTreeNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorTreeNumber


class TypeDescriptorSynonym(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorSynonym


class TypeConcept(SQLAlchemyObjectType):
    class Meta:
        model = ModelConcept


class TypeQualifier(SQLAlchemyObjectType):
    class Meta:
        model = ModelQualifier


class TypeDescriptorDefinition(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorDefinition
