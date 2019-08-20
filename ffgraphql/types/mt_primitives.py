# coding=utf-8

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_mt import (
    DescriptorClassType as EnumDescriptorClass,
    RelationNameType as EnumRelationName,
    LexicalTagType as EnumLexicalTag,
    EntryCombinationType as EnumEntryCombination,
    SupplementalClassType as EnumSupplementalClass,
    DescriptorDefinitionSourceType as EnumDescriptorDefinitionSource,
    TreeNumber as ModelTreeNumber,
    ThesaurusId as ModelThesaurusId,
    Term as ModelTerm,
    TermThesaurusId as ModelTermThesaurusId,
    RelatedRegistryNumber as ModelRelatedRegistryNumber,
    Concept as ModelConcept,
    ConceptRelatedRegistryNumber as ModelConceptRelatedRegistryNumber,
    ConceptRelatedConcept as ModelConceptRelatedConcept,
    ConceptTerm as ModelConceptTerm,
    Qualifier as ModelQualifier,
    QualifierConcept as ModelQualifierConcept,
    QualifierTreeNumber as ModelQualifierTreeNumber,
    PreviousIndexing as ModelPreviousIndexing,
    EntryCombination as ModelEntryCombination,
    Descriptor as ModelDescriptor,
    DescriptorEntryCombination as ModelDescriptorEntryCombination,
    DescriptorConcept as ModelDescriptorConcept,
    DescriptorPreviousIndexing as ModelDescriptorPreviousIndexing,
    DescriptorAllowableQualifier as ModelDescriptorAllowableQualifier,
    DescriptorTreeNumber as ModelDescriptorTreeNumber,
    DescriptorPharmacologicalActionDescriptor as ModelDescriptorPharmacologicalActionDescriptor,
    DescriptorRelatedDescriptor as ModelDescriptorRelatedDescriptor,
    Source as ModelSource,
    Supplemental as ModelSupplemental,
    SupplementalHeadingMappedTo as ModelSupplementalHeadingMappedTo,
    SupplementalIndexingInformation as ModelSupplementalIndexingInformation,
    SupplementalConcept as ModelSupplementalConcept,
    SupplementalPreviousIndexing as ModelSupplementalPreviousIndexing,
    SupplementalPharmacologicalActionDescriptor as ModelSupplementalPharmacologicalActionDescriptor,
    SupplementalSource as ModelSupplementalSource,
    DescriptorSynonym as ModelDescriptorSynonym,
    DescriptorDefinition as ModelDescriptorDefinition,
)


TypeEnumDescriptorClass = graphene.Enum.from_enum(EnumDescriptorClass)
TypeEnumRelationName = graphene.Enum.from_enum(EnumRelationName)
TypeEnumLexicalTag = graphene.Enum.from_enum(EnumLexicalTag)
TypeEnumEntryCombination = graphene.Enum.from_enum(EnumEntryCombination)
TypeEnumSupplementalClass = graphene.Enum.from_enum(EnumSupplementalClass)
TypeEnumDescriptorDefinitionSource = graphene.Enum.from_enum(
    EnumDescriptorDefinitionSource,
)


class TypeTreeNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelTreeNumber


class TypeThesaurusId(SQLAlchemyObjectType):
    class Meta:
        model = ModelThesaurusId


class TypeTerm(SQLAlchemyObjectType):
    class Meta:
        model = ModelTerm


class TypeTermThesaurusId(SQLAlchemyObjectType):
    class Meta:
        model = ModelTermThesaurusId


class TypeRelatedRegistryNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelRelatedRegistryNumber


class TypeConcept(SQLAlchemyObjectType):
    class Meta:
        model = ModelConcept


class TypeConceptRelatedRegistryNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelConceptRelatedRegistryNumber


class TypeConceptRelatedConcept(SQLAlchemyObjectType):

    relation_name = TypeEnumRelationName()

    class Meta:
        model = ModelConceptRelatedConcept
        exclude_fields = ["relation_name"]

    def resolve_relation_name(self, info, **kwargs):
        return self.relation_name


class TypeConceptTerm(SQLAlchemyObjectType):

    lexical_tag = TypeEnumLexicalTag()

    class Meta:
        model = ModelConceptTerm
        exclude_fields = ["lexical_tag"]

    def resolve_lexical_tag(self, info, **kwargs):
        return self.lexical_tag


class TypeQualifier(SQLAlchemyObjectType):
    class Meta:
        model = ModelQualifier


class TypeQualifierConcept(SQLAlchemyObjectType):
    class Meta:
        model = ModelQualifierConcept


class TypeQualifierTreeNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelQualifierTreeNumber


class TypePreviousIndexing(SQLAlchemyObjectType):
    class Meta:
        model = ModelPreviousIndexing


class TypeEntryCombination(SQLAlchemyObjectType):

    combination_type = TypeEnumEntryCombination()

    class Meta:
        model = ModelEntryCombination
        exclude_fields = ["combination_type"]

    def resolve_combination_type(self, info, **kwargs):
        return self.combination_type


class TypeDescriptor(SQLAlchemyObjectType):

    descriptor_class = TypeEnumDescriptorClass()

    class Meta:
        model = ModelDescriptor
        exclude_fields = ["descriptor_class"]

    def resolve_descriptor_class(self, info, **kwargs):
        return self.descriptor_class


class TypeDescriptorEntryCombination(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorEntryCombination


class TypeDescriptorConcept(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorConcept


class TypeDescriptorPreviousIndexing(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorPreviousIndexing


class TypeDescriptorAllowableQualifier(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorAllowableQualifier


class TypeDescriptorTreeNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorTreeNumber


class TypeDescriptorPharmacologicalActionDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorPharmacologicalActionDescriptor


class TypeDescriptorRelatedDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorRelatedDescriptor


class TypeSource(SQLAlchemyObjectType):
    class Meta:
        model = ModelSource


class TypeSupplemental(SQLAlchemyObjectType):

    supplemental_class = TypeEnumSupplementalClass()

    class Meta:
        model = ModelSupplemental
        exclude_fields = ["supplemental_classsource"]

    def resolve_supplemental_class(self, info, **kwargs):
        return self.supplemental_class


class TypeSupplementalHeadingMappedTo(SQLAlchemyObjectType):
    class Meta:
        model = ModelSupplementalHeadingMappedTo


class TypeSupplementalIndexingInformation(SQLAlchemyObjectType):
    class Meta:
        model = ModelSupplementalIndexingInformation


class TypeSupplementalConcept(SQLAlchemyObjectType):
    class Meta:
        model = ModelSupplementalConcept


class TypeSupplementalPreviousIndexing(SQLAlchemyObjectType):
    class Meta:
        model = ModelSupplementalPreviousIndexing


class TypeSupplementalPharmacologicalActionDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelSupplementalPharmacologicalActionDescriptor


class TypeSupplementalSource(SQLAlchemyObjectType):
    class Meta:
        model = ModelSupplementalSource


class TypeDescriptorSynonym(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptorSynonym


class TypeDescriptorDefinition(SQLAlchemyObjectType):

    source = TypeEnumDescriptorDefinitionSource()

    class Meta:
        model = ModelDescriptorDefinition
        exclude_fields = ["source"]

    def resolve_source(self, info, **kwargs):
        return self.source
