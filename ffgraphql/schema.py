# coding=utf-8

import graphene

from ffgraphql.types.studies import StudyType
from ffgraphql.types.studies import StudiesType


class Query(graphene.ObjectType):


    studies = graphene.Field(
        type=StudiesType,
        description="Clinical-trials studies.",
    )

    study_stats = graphene.Field(
        type=TypeStudyStats,
        description="Clinical-trial study-related statistics."
    )

    @staticmethod

    @staticmethod
    def resolve_studies(args, info):
        return StudiesType

    @staticmethod
    def resolve_study_stats(args, info):
        return TypeStudyStats


schema = graphene.Schema(
    query=Query,
    types=[
        StudyType,
        StudiesType,
    ]
)
