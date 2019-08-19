# coding=utf-8

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_mt import (
    Descriptor as ModelDescriptor,
    TreeNumber as ModelTreeNumber,
    DescriptorTreeNumber as ModelDescriptorTreeNumber,
    DescriptorSynonym as ModelDescriptorSynonym,
    Concept as ModelConcept,
    Qualifier as ModelQualifier,
    DescriptorDefinition as ModelDescriptorDefinition,
    DescriptorClassType as EnumDescriptorClass,
    DescriptorDefinitionSourceType as EnumDescriptorDefinitionSource,
)


TypeEnumDescriptorClass = graphene.Enum.from_enum(EnumDescriptorClass)
TypeEnumDescriptorDefinitionSource = graphene.Enum.from_enum(
    EnumDescriptorDefinitionSource,
)


class TypeDescriptor(SQLAlchemyObjectType):

    descriptor_class = TypeEnumDescriptorClass()

    class Meta:
        model = ModelDescriptor
        exclude_fields = ["descriptor_class"]

    def resolve_descriptor_class(self, info, **kwargs):
        return self.descriptor_class


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

    source = TypeEnumDescriptorDefinitionSource()

    class Meta:
        model = ModelDescriptorDefinition
        exclude_fields = ["source"]

    def resolve_source(self, info, **kwargs):
        return self.source
