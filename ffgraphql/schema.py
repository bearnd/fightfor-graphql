# coding=utf-8

import graphene

from ffgraphql.types.ct_primitives import TypeStudy
from ffgraphql.types.ct_primitives import TypeMeshTerm
from ffgraphql.types.ct_primitives import TypeLocation
from ffgraphql.types.ct_primitives import TypeFacility
from ffgraphql.types.ct_primitives import TypeFacilityCanonical
from ffgraphql.types.ct_primitives import TypeIntervention
from ffgraphql.types.ct_primitives import TypeCondition
from ffgraphql.types.ct_primitives import TypeStudyMeshTerm
from ffgraphql.types.ct_primitives import TypeEligibility
from ffgraphql.types.mt_primitives import TypeDescriptor
from ffgraphql.types.mt_primitives import TypeTreeNumber
from ffgraphql.types.mt_primitives import TypeDescriptorSynonym
from ffgraphql.types.mt_primitives import TypeConcept
from ffgraphql.types.mt_primitives import TypeQualifier
from ffgraphql.types.pubmed_primitives import TypeCitation
from ffgraphql.types.pubmed_primitives import TypeAffiliationCanonical
from ffgraphql.types.studies import TypeStudies
from ffgraphql.types.descriptors import TypeDescriptors
from ffgraphql.types.studies_stats import TypeCountStudiesCountry
from ffgraphql.types.studies_stats import TypeCountStudiesFacility
from ffgraphql.types.studies_stats import TypeCountStudiesOverallStatus
from ffgraphql.types.studies_stats import TypeCountStudiesFacilityMeshTerm
from ffgraphql.types.studies_stats import TypeDateRange
from ffgraphql.types.studies_stats import TypeAgeRange
from ffgraphql.types.studies_stats import TypeStudiesStats
from ffgraphql.types.citations import TypeCitations
from ffgraphql.types.citations_stats import TypeCountCitationsCountry
from ffgraphql.types.citations_stats import TypeCountCitationsAffiliation
from ffgraphql.types.citations_stats import TypeCitationsStats


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
        TypeStudy,
        TypeStudies,
        TypeMeshTerm,
        TypeLocation,
        TypeFacility,
        TypeFacilityCanonical,
        TypeIntervention,
        TypeCondition,
        TypeStudyMeshTerm,
        TypeEligibility,
        TypeDescriptor,
        TypeDescriptors,
        TypeDescriptorSynonym,
        TypeConcept,
        TypeQualifier,
        TypeCountStudiesCountry,
        TypeCountStudiesFacility,
        TypeCountStudiesOverallStatus,
        TypeCountStudiesFacilityMeshTerm,
        TypeDateRange,
        TypeAgeRange,
        TypeStudiesStats,
        TypeTreeNumber,
        TypeCitation,
        TypeCitations,
        TypeAffiliationCanonical,
        TypeCitationsStats,
        TypeCountCitationsCountry,
        TypeCountCitationsAffiliation,
    ]
)
