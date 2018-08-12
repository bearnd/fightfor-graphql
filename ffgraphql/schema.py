# coding=utf-8

import graphene

from ffgraphql.types.ct_primitives import TypeStudy
from ffgraphql.types.ct_primitives import TypeMeshTerm
from ffgraphql.types.ct_primitives import TypeLocation
from ffgraphql.types.ct_primitives import TypeFacility
from ffgraphql.types.ct_primitives import TypeIntervention
from ffgraphql.types.ct_primitives import TypeCondition
from ffgraphql.types.ct_primitives import TypeStudyMeshTerm
from ffgraphql.types.mt_primitives import TypeDescriptor
from ffgraphql.types.mt_primitives import TypeTreeNumber
from ffgraphql.types.mt_primitives import TypeDescriptorSynonym
from ffgraphql.types.mt_primitives import TypeConcept
from ffgraphql.types.mt_primitives import TypeQualifier
from ffgraphql.types.studies import TypeStudies
from ffgraphql.types.descriptors import TypeDescriptors
from ffgraphql.types.studies_stats import TypeCountStudiesCountry
from ffgraphql.types.studies_stats import TypeCountStudiesFacility
from ffgraphql.types.studies_stats import TypeCountStudiesOverallStatus
from ffgraphql.types.studies_stats import TypeDateRange
from ffgraphql.types.studies_stats import TypeAgeRange
from ffgraphql.types.studies_stats import TypeStudiesStats


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

    @staticmethod
    def resolve_studies_stats(args, info):
        return TypeStudiesStats

    @staticmethod
    def resolve_studies(args, info):
        return TypeStudies

    @staticmethod
    def resolve_descriptors(args, info):
        return TypeDescriptors


schema = graphene.Schema(
    query=Query,
    types=[
        TypeStudy,
        TypeStudies,
        TypeMeshTerm,
        TypeLocation,
        TypeFacility,
        TypeIntervention,
        TypeCondition,
        TypeStudyMeshTerm,
        TypeDescriptor,
        TypeDescriptors,
        TypeDescriptorSynonym,
        TypeConcept,
        TypeQualifier,
        TypeCountStudiesCountry,
        TypeCountStudiesFacility,
        TypeCountStudiesOverallStatus,
        TypeDateRange,
        TypeAgeRange,
        TypeStudiesStats,
        TypeTreeNumber,
    ]
)
