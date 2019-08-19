# coding=utf-8

from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_mt import (
    Descriptor as ModelDescriptor,
    TreeNumber as ModelTreeNumber,
    DescriptorTreeNumber as ModelDescriptorTreeNumber,
    DescriptorSynonym as ModelDescriptorSynonym,
    Concept as ModelConcept,
    Qualifier as ModelQualifier,
    DescriptorDefinition as ModelDescriptorDefinition,
)


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
