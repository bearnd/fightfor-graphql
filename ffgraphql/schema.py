# coding=utf-8

import graphene

from ffgraphql.types.studies import StudyType
from ffgraphql.types.studies import StudiesType
from ffgraphql.types.descriptors import DescriptorType
from ffgraphql.types.descriptors import DescriptorsType


class Query(graphene.ObjectType):


    studies = graphene.Field(
        type=StudiesType,
        description="Clinical-trials studies.",
    )

    study_stats = graphene.Field(
        type=TypeStudyStats,
        description="Clinical-trial study-related statistics."
    descriptors = graphene.Field(
        type=DescriptorsType,
        description="MeSH descriptors.",
    )

    @staticmethod

    @staticmethod
    def resolve_studies(args, info):
        return StudiesType

    @staticmethod
    def resolve_study_stats(args, info):
        return TypeStudyStats
    def resolve_descriptors(args, info):
        return DescriptorsType


schema = graphene.Schema(
    query=Query,
    types=[
        StudyType,
        StudiesType,
        DescriptorType,
        DescriptorsType,
    ]
)
