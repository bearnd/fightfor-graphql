# coding=utf-8

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_pubmed import Citation as ModelCitation
from fform.orm_pubmed import Article as ModelArticle
from fform.orm_pubmed import (
    ArticleAuthorAffiliation as ModelArticleAuthorAffiliation
)
from fform.orm_pubmed import JournalInfo as ModelJournalInfo
from fform.orm_pubmed import Journal as ModelJournal
from fform.orm_pubmed import Chemical as ModelChemical
from fform.orm_pubmed import PmDescriptor as ModelPmDescriptor
from fform.orm_pubmed import PmQualifier as ModelPmQualifier
from fform.orm_pubmed import (
    CitationDescriptorQualifier as ModelCitationDescriptorQualifier
)
from fform.orm_pubmed import AffiliationCanonical as ModelAffiliationCanonical
from fform.orm_pubmed import JournalIssnType as EnumJournalIssn


class TypeCitation(SQLAlchemyObjectType):
    class Meta:
        model = ModelCitation


class TypeArticle(SQLAlchemyObjectType):
    class Meta:
        model = ModelArticle


class TypeJournalInfo(SQLAlchemyObjectType):
    class Meta:
        model = ModelJournalInfo


class TypeJournal(SQLAlchemyObjectType):
    class Meta:
        model = ModelJournal


class TypeChemical(SQLAlchemyObjectType):
    class Meta:
        model = ModelChemical


class TypePubMedDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelPmDescriptor


class TypePubMedQualifier(SQLAlchemyObjectType):
    class Meta:
        model = ModelPmQualifier


class TypeCitationDescriptorQualifier(SQLAlchemyObjectType):
    class Meta:
        model = ModelCitationDescriptorQualifier


class TypeAffiliationCanonical(SQLAlchemyObjectType):
    class Meta:
        model = ModelAffiliationCanonical


class TypeArticleAuthorAffiliation(SQLAlchemyObjectType):
    class Meta:
        model = ModelArticleAuthorAffiliation


TypeEnumJournalIssn = graphene.Enum.from_enum(EnumJournalIssn)
