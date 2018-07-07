# coding=utf-8

from typing import List, Optional

import sqlalchemy.orm
import graphene
from sqlalchemy import func as sqlalchemy_func
from fform.orm_ct import Study as StudyModel
from fform.orm_ct import Location as LocationModel
from fform.orm_ct import Facility as FacilityModel
from fform.orm_ct import OverallStatusType as OverallStatusEnum

from ffgraphql.types.facilities import FacilityType
from ffgraphql.utils import extract_requested_fields
from ffgraphql.utils import apply_requested_fields


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


class TypeCountStudiesFacility(graphene.ObjectType):
    """Graphene type representing a single result of an aggregation operation
    calculating the number of clinical-trial studies by facility."""

    facility = graphene.Field(
        type=FacilityType,
        description="The facility in which the studies are performed."
    )

    count_studies = graphene.Int(description="The number of studies.")


class TypeStudiesStats(graphene.ObjectType):

    count_studies_by_country = graphene.List(
        of_type=TypeCountStudiesCountry,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True
        ),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    count_studies_by_overall_status = graphene.List(
        of_type=TypeCountStudiesOverallStatus,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True
        ),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    count_studies_by_facility = graphene.List(
        of_type=TypeCountStudiesFacility,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True
        ),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    @staticmethod
    def resolve_count_studies_by_country(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
        limit: Optional[int] = None,
    ) -> List[TypeCountStudiesCountry]:
        """Creates a list of `TypeCountStudiesCountry` objects with the number
        of clinical-trial studies per country.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.
            limit (Optional[int]): The number of results to return. Defaults to
                `None` in which case all results are returned.

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
        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

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
        limit: Optional[int] = None,
    ) -> List[TypeCountStudiesOverallStatus]:
        """Creates a list of `TypeCountStudiesOverallStatus` objects with the
        number of clinical-trial studies per overall-status.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.
            limit (Optional[int]): The number of results to return. Defaults to
                `None` in which case all results are returned.

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
        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

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

    @staticmethod
    def resolve_count_studies_by_facility(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
        limit: Optional[int] = None,
    ) -> List[TypeCountStudiesFacility]:
        """Creates a list of `TypeCountStudiesFacility` objects with the number
        of clinical-trial studies per facility.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.
            limit (Optional[int]): The number of results to return. Defaults to
                `None` in which case all results are returned.

        Returns:
             list[TypeCountStudiesFacility]: The list of
                `TypeCountStudiesFacility` objects with the results of the
                aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(studies.study_id)` function.
        func_count_studies = sqlalchemy_func.count(StudyModel.study_id)

        # Query out the count of studies by facility.
        query = session.query(
            FacilityModel,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.join(StudyModel.locations)
        query = query.filter(StudyModel.study_id.in_(study_ids))
        query = query.join(
            FacilityModel,
            LocationModel.facility_id == FacilityModel.facility_id
        )
        # Group by study facility.
        query = query.group_by(FacilityModel.facility_id)

        # Extract the fields requested in the GraphQL query.
        fields = extract_requested_fields(
            info=info,
            fields=info.field_asts,
            do_convert_to_snake_case=True,
        )["count_studies_by_facility"]["facility"]

        # Limit query to `Facility` fields requested in the GraphQL query.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=FacilityModel,
            fields={"facility": fields},
        )

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        results = query.all()

        # Wrap the results of the aggregation in `TypeCountStudiesFacility`
        # objects.
        objs = [
            TypeCountStudiesFacility(
                facility=result[0],
                count_studies=result[1]
            ) for result in results
        ]

        return objs
