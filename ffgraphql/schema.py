# coding=utf-8

import datetime
from typing import Union, List

import graphene
from fform.orm_ct import Study
from fform.orm_ct import MeshTerm

from ffgraphql.schema_types import TypeStudy
from ffgraphql.schema_types import TypeAlias
from ffgraphql.schema_types import TypeSponsor
from ffgraphql.schema_types import TypeMeshTerm
from ffgraphql.schema_types import TypeStudyStats


class Query(graphene.ObjectType):

    study = graphene.Field(
        type=TypeStudy,
        description="A clinical-trial study",
        nct_id=graphene.Argument(type=graphene.String, required=True),
    )

    studies = graphene.List(
        of_type=TypeStudy,
        description="A list of clinical-trial studies",
        mesh_terms=graphene.Argument(
            type=graphene.List(of_type=graphene.String),
            required=False
        ),
        year_beg=graphene.Argument(type=graphene.Int, required=False),
        year_end=graphene.Argument(type=graphene.Int, required=False),
    )

    study_stats = graphene.Field(
        type=TypeStudyStats,
        description="Clinical-trial study-related statistics."
    )

    @staticmethod
    def resolve_study(
        args,
        info,
        nct_id: str
    ):
        query = TypeStudy.get_query(info=info)
        query = query.filter(Study.nct_id == nct_id)

        obj = query.first()

        return obj

    @staticmethod
    def resolve_studies(
        args,
        info,
        mesh_terms: Union[List[str], None] = None,
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
    ):
        query = TypeStudy.get_query(info=info)

        if mesh_terms:
            query = query.filter(MeshTerm.term.in_(mesh_terms))

        if year_beg:
            query = query.filter(
                Study.start_date >= datetime.date(year_beg, 1, 1)
            )

        if year_end:
            query = query.filter(
                Study.start_date <= datetime.date(year_end, 12, 31)
            )

        objs = query.all()

        return objs

    @staticmethod
    def resolve_study_stats(args, info):
        return TypeStudyStats


schema = graphene.Schema(
    query=Query,
    types=[
        TypeStudy,
        TypeAlias,
        TypeSponsor,
        TypeMeshTerm,
        TypeStudyStats,
    ]
)
