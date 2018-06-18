# coding=utf-8

import hashlib
import datetime
from typing import Union, List

import sqlalchemy.orm
import graphene
from sqlalchemy import func as sqlalchemy_func
from fform.orm_ct import Study as StudyModel
from fform.orm_ct import Location as LocationModel
from fform.orm_ct import Facility as FacilityModel
from fform.orm_ct import MeshTerm as MeshTermModel
from fform.orm_ct import OverallStatusType as OverallStatusEnum


class TypeCountStudiesCountry(graphene.ObjectType):
    """Graphene type representing a single result of an aggregation operation
    calculating the number of clinical-trial studies by country."""

    country = graphene.String(
        description="The country in which the studies are performed."
    )

    count_studies = graphene.Int(description="The number of studies.")


class TypeCountStudiesOverallStatus(graphene.ObjectType):
    """Graphene type representing a single result of an aggregation operation
    calculating the number of clinical-trial studies by overall-status."""

    overall_status = graphene.String(
        description="The overall-status of the studies."
    )

    count_studies = graphene.Int(description="The number of studies.")


class TypeStudiesStats(graphene.ObjectType):

    count_studies_by_country = graphene.List(
        of_type=TypeCountStudiesCountry,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True
        ),
    )

    count_studies_by_overall_status = graphene.List(
        of_type=TypeCountStudiesOverallStatus,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True
        ),
    )

    @staticmethod
    def resolve_count_studies_by_country(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
    ) -> List[TypeCountStudiesCountry]:
        """Creates a list of `TypeCountStudiesCountry` objects with the number
        of clinical-trial studies per country.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.

        Returns:
             list[TypeCountStudiesCountry]: The list of
                `TypeCountStudiesCountry` objects with the results of the
                aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(studies.study_id)` function.
        func_count_studies = sqlalchemy_func.count(StudyModel.study_id)

        # Query out the count of studies by country.
        query = session.query(
            FacilityModel.country,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.join(StudyModel.locations)
        query = query.filter(StudyModel.study_id.in_(study_ids))
        query = query.join(
            FacilityModel,
            LocationModel.facility_id == FacilityModel.facility_id
        )
        # Group by study overall-status.
        query = query.group_by(FacilityModel.country)

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

    @staticmethod
    def resolve_count_studies_by_overall_status(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
    ) -> List[TypeCountStudiesOverallStatus]:
        """Creates a list of `TypeCountStudiesOverallStatus` objects with the
        number of clinical-trial studies per overall-status.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.

        Returns:
             list[TypeCountStudiesOverallStatus]: The list of
                `TypeCountStudiesOverallStatus` objects with the results of the
                aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(studies.study_id)` function.
        func_count_studies = sqlalchemy_func.count(StudyModel.study_id)

        # Query out the count of studies by overall-status.
        query = session.query(
            StudyModel.overall_status,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.filter(StudyModel.study_id.in_(study_ids))
        # Group by study overall-status.
        query = query.group_by(StudyModel.overall_status)

        results = query.all()

        # Wrap the results of the aggregation in `TypeCountStudiesOverallStatus`
        # objects.
        objs = [
            TypeCountStudiesOverallStatus(
                overall_status=OverallStatusEnum(result[0]).value,
                count_studies=result[1]
            ) for result in results
        ]

        return objs
