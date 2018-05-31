# coding=utf-8

from typing import List

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
import sqlalchemy.orm
from sqlalchemy import func as sqlalchemy_func
from fform.orm_ct import Study
from fform.orm_ct import Alias
from fform.orm_ct import Sponsor
from fform.orm_ct import MeshTerm
from fform.orm_ct import Location
from fform.orm_ct import Facility


class TypeStudy(SQLAlchemyObjectType):
    class Meta:
        model = Study


class TypeAlias(SQLAlchemyObjectType):
    class Meta:
        model = Alias


class TypeSponsor(SQLAlchemyObjectType):
    class Meta:
        model = Sponsor


class TypeMeshTerm(SQLAlchemyObjectType):
    class Meta:
        model = MeshTerm


class TypeCountStudiesCountry(graphene.ObjectType):
    """Graphene type representing a single result of an aggregation operation
    calculating the number of clinical-trial studies by country."""

    country = graphene.String(
        description="The country in which the studies are performed."
    )

    count_studies = graphene.Int(description="The number of studies.")


class TypeStudyStats(graphene.ObjectType):

    count_studies_by_country = graphene.List(
        of_type=TypeCountStudiesCountry
    )

    @staticmethod
    def resolve_count_studies_by_country(
        args,
        info
    ) -> List[TypeCountStudiesCountry]:
        """"""

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(studies.study_id)` function.
        func_count_studies = sqlalchemy_func.count(Study.study_id)

        # Query out the count of studies by country.
        query = session.query(
            Facility.country,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.join(Study.locations)
        query = query.join(
            Facility,
            Location.facility_id == Facility.facility_id
        )
        query = query.group_by(Facility.country)
        results = query.all()

        # Wrap the results of the aggregation in `TypeCountStudiesCountry`
        # objects.
        objs = [
            TypeCountStudiesCountry(
                country=result[0],
                count_studies=result[1]
            ) for result in results
        ]

        return objs
