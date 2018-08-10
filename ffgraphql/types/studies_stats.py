# coding=utf-8

from typing import List, Optional

import sqlalchemy.orm
import graphene
from sqlalchemy import func as sqlalchemy_func

from ffgraphql.types.ct_primitives import ModelStudy
from ffgraphql.types.ct_primitives import ModelLocation
from ffgraphql.types.ct_primitives import ModelFacility
from ffgraphql.types.ct_primitives import TypeFacility
from ffgraphql.types.ct_primitives import EnumOverallStatus
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
        type=TypeFacility,
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

    get_unique_cities = graphene.List(
        of_type=graphene.String,
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
        func_count_studies = sqlalchemy_func.count(ModelStudy.study_id)

        # Query out the count of studies by country.
        query = session.query(
            ModelFacility.country,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.join(ModelStudy.locations)
        query = query.filter(ModelStudy.study_id.in_(study_ids))
        query = query.join(
            ModelFacility,
            ModelLocation.facility_id == ModelFacility.facility_id
        )
        # Group by study overall-status.
        query = query.group_by(ModelFacility.country)
        # Order by the number of studies.
        query = query.order_by(func_count_studies.desc())

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
        func_count_studies = sqlalchemy_func.count(ModelStudy.study_id)

        # Query out the count of studies by overall-status.
        query = session.query(
            ModelStudy.overall_status,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.filter(ModelStudy.study_id.in_(study_ids))
        # Group by study overall-status.
        query = query.group_by(ModelStudy.overall_status)
        # Order by the number of studies.
        query = query.order_by(func_count_studies.desc())

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        results = query.all()

        # Wrap the results of the aggregation in `TypeCountStudiesOverallStatus`
        # objects.
        objs = [
            TypeCountStudiesOverallStatus(
                overall_status=EnumOverallStatus(result[0]).value,
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
        func_count_studies = sqlalchemy_func.count(ModelStudy.study_id)

        # Query out the count of studies by facility.
        query = session.query(
            ModelFacility,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.join(ModelStudy.locations)
        query = query.filter(ModelStudy.study_id.in_(study_ids))
        query = query.join(
            ModelFacility,
            ModelLocation.facility_id == ModelFacility.facility_id
        )
        # Group by study facility.
        query = query.group_by(ModelFacility.facility_id)
        # Order by the number of studies.
        query = query.order_by(func_count_studies.desc())

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
            orm_class=ModelFacility,
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

    @staticmethod
    def resolve_get_unique_cities(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
    ) -> List[str]:
        """Retrieves a list of unique cities out of a list of clinical-trial
        studies.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.

        Returns:
             list[str]: The list of unique cities.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `DISTINCT(facilities.city)` function.
        func_unique_cities = sqlalchemy_func.distinct(ModelFacility.city)

        # Query out the unique cities of the studies.
        query = session.query(func_unique_cities)  # type: sqlalchemy.orm.Query
        query = query.join(ModelStudy.locations)
        query = query.filter(ModelStudy.study_id.in_(study_ids))
        query = query.join(
            ModelFacility,
            ModelLocation.facility_id == ModelFacility.facility_id
        )

        results = query.all()

        # Unpack the cities out of the results.
        cities = [result[0] for result in results]

        return cities

