# coding=utf-8

import graphene

from ffgraphql.types.studies import StudyType
from ffgraphql.types.studies import StudiesType
from ffgraphql.types.descriptors import DescriptorType
from ffgraphql.types.descriptors import DescriptorsType
from ffgraphql.types.study_stats import TypeCountStudiesCountry
from ffgraphql.types.study_stats import TypeStudiesStats


class Query(graphene.ObjectType):

    studies_stats = graphene.Field(
        type=TypeStudiesStats,
        description="Clinical-trial study-related statistics."
    )

    studies = graphene.Field(
        type=StudiesType,
        description="Clinical-trials studies.",
    )

    descriptors = graphene.Field(
        type=DescriptorsType,
        description="MeSH descriptors.",
    )

    @staticmethod
    def resolve_studies_stats(args, info):
        return TypeStudiesStats

    @staticmethod
    def resolve_studies(args, info):
        return StudiesType

    @staticmethod
    def resolve_descriptors(args, info):
        return DescriptorsType


schema = graphene.Schema(
    query=Query,
    types=[
        StudyType,
        StudiesType,
        DescriptorType,
        DescriptorsType,
        TypeCountStudiesCountry,
        TypeStudiesStats,
    ]
)
