# coding=utf-8

import graphene

from ffgraphql.types.ct_primitives import (
    TypeEnumOverallStatus,
    TypeStudy,
    TypeMeshTerm,
    TypeLocation,
    TypeFacility,
    TypeFacilityCanonical,
    TypeIntervention,
    TypeCondition,
    TypeStudyMeshTerm,
    TypeEligibility,
    TypeStudyFacility,
    TypeEnumOrder,
    TypeEnumIntervention,
    TypeEnumPhase,
    TypeEnumStudy,
    TypeEnumGender,
    TypeEnumMeshTerm,
)
from ffgraphql.types.mt_primitives import (
    TypeDescriptor,
    TypeTreeNumber,
    TypeDescriptorSynonym,
    TypeConcept,
    TypeQualifier,
)
from ffgraphql.types.pubmed_primitives import (
    TypeCitation,
    TypeArticle,
    TypeJournalInfo,
    TypeJournal,
    TypeChemical,
    TypePubMedDescriptor,
    TypePubMedQualifier,
    TypeCitationDescriptorQualifier,
    TypeAffiliationCanonical,
    TypeArticleAuthorAffiliation,
    TypeEnumJournalIssn,
)
from ffgraphql.types.studies import TypeStudies
from ffgraphql.types.descriptors import TypeDescriptors
from ffgraphql.types.citations import TypeCitations
from ffgraphql.types.studies_stats import (
    TypeCountStudiesCountry,
    TypeCountStudiesOverallStatus,
    TypeCountStudiesFacility,
    TypeCountStudiesFacilityMeshTerm,
    TypeDateRange,
    TypeAgeRange,
    TypeStudiesStats,
)
from ffgraphql.types.citations_stats import (
    TypeCountCitationsCountry,
    TypeCountCitationsAffiliation,
    TypeCitationsStats,
)


class Query(graphene.ObjectType):

    studies_stats = graphene.Field(
        type=TypeStudiesStats,
        description="Clinical-trial study-related statistics."
    )

    studies = graphene.Field(
        type=TypeStudies,
        description="Clinical-trials studies.",
    )

    descriptors = graphene.Field(
        type=TypeDescriptors,
        description="MeSH descriptors.",
    )

    citations = graphene.Field(
        type=TypeCitations,
        description="PubMed citations.",
    )

    citations_stats = graphene.Field(
        type=TypeCitationsStats,
        description="PubMed citation-related statistics.",
    )

    @staticmethod
    def resolve_studies_stats(args, info):
        return TypeStudiesStats

    @staticmethod
    def resolve_studies(args, info):
        return TypeStudies

    @staticmethod
    def resolve_descriptors(args, info):
        return TypeDescriptors

    @staticmethod
    def resolve_citations(args, info):
        return TypeCitations

    @staticmethod
    def resolve_citations_stats(args, info):
        return TypeCitationsStats


schema = graphene.Schema(
    query=Query,
    types=[
        # Clinical-trial primitives.
        TypeEnumOverallStatus,
        TypeStudy,
        TypeMeshTerm,
        TypeLocation,
        TypeFacility,
        TypeFacilityCanonical,
        TypeIntervention,
        TypeCondition,
        TypeStudyMeshTerm,
        TypeEligibility,
        TypeStudyFacility,
        TypeEnumOrder,
        TypeEnumIntervention,
        TypeEnumPhase,
        TypeEnumStudy,
        TypeEnumGender,
        TypeEnumMeshTerm,
        # MeSH term primitives.
        TypeDescriptor,
        TypeTreeNumber,
        TypeDescriptorSynonym,
        TypeConcept,
        TypeQualifier,
        # PubMed primitives.
        TypeCitation,
        TypeArticle,
        TypeJournalInfo,
        TypeJournal,
        TypeChemical,
        TypePubMedDescriptor,
        TypePubMedQualifier,
        TypeCitationDescriptorQualifier,
        TypeAffiliationCanonical,
        TypeArticleAuthorAffiliation,
        TypeEnumJournalIssn,
        # Clinical trials studies.
        TypeStudies,
        # MeSH descriptors.
        TypeDescriptors,
        # PubMed citations.
        TypeCitations,
        # Clinical trials study statistics.
        TypeCountStudiesCountry,
        TypeCountStudiesOverallStatus,
        TypeCountStudiesFacility,
        TypeCountStudiesFacilityMeshTerm,
        TypeDateRange,
        TypeAgeRange,
        TypeStudiesStats,
        # PubMed citation statistics.
        TypeCountCitationsCountry,
        TypeCountCitationsAffiliation,
        TypeCitationsStats,
    ]
)
