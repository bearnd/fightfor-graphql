# coding=utf-8

from typing import List, Optional

import sqlalchemy.orm
import graphene
from sqlalchemy import func as sqlalchemy_func
from sqlalchemy.dialects import postgresql
from graphene.utils.str_converters import to_snake_case

from ffgraphql.types.ct_primitives import ModelStudy
from ffgraphql.types.ct_primitives import ModelStudyFacility
from ffgraphql.types.ct_primitives import ModelFacilityCanonical
from ffgraphql.types.ct_primitives import ModelEligibility
from ffgraphql.types.ct_primitives import TypeFacilityCanonical
from ffgraphql.types.ct_primitives import EnumOverallStatus
from ffgraphql.types.ct_primitives import ModelStudyDescriptor
from ffgraphql.types.ct_primitives import TypeEnumMeshTerm
from ffgraphql.types.ct_primitives import EnumMeshTerm
from ffgraphql.types.ct_primitives import TypeEnumOverallStatus
from ffgraphql.types.ct_primitives import TypeEnumOrder
from ffgraphql.types.mt_primitives import ModelDescriptor
from ffgraphql.types.mt_primitives import TypeDescriptor
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
    calculating the number of clinical-trial studies by canonical facility."""

    facility_canonical = graphene.Field(
        type=TypeFacilityCanonical,
        description="The canonical facility in which the studies are "
                    "performed.",
    )

    count_studies = graphene.Int(description="The number of studies.")


class TypeCountStudiesFacilityDescriptor(graphene.ObjectType):
    """ Graphene type representing a single result of an aggregation operation
        calculating the number of clinical-trial studies canonical facility and
        MeSH descriptor.
    """

    facility_canonical = graphene.Field(
        type=TypeFacilityCanonical,
        description="The canonical facility in which the studies are "
                    "performed.",
    )

    mesh_term = graphene.Field(
        type=TypeDescriptor,
        description="The MeSH descriptor with which the studies are tagged.",
    )

    count_studies = graphene.Int(description="The number of studies.")


class TypeCountStudiesDescriptor(graphene.ObjectType):
    """ Graphene type representing a single result of an aggregation operation
        calculating the number of clinical-trial studies by MeSH descriptor.
    """

    mesh_term = graphene.Field(
        type=TypeDescriptor,
        description="The MeSH descriptor with which the studies are tagged.",
    )

    count_studies = graphene.Int(description="The number of studies.")


class TypeDateRange(graphene.ObjectType):
    """Graphene type representing a date-range."""

    date_beg = graphene.Field(
        type=graphene.Date,
        description="The beginning of the date-range."
    )

    date_end = graphene.Field(
        type=graphene.Date,
        description="The end of the date-range."
    )


class TypeAgeRange(graphene.ObjectType):
    """Graphene type representing an age-range in seconds."""

    age_beg = graphene.Field(
        type=graphene.Float,
        description="The beginning of the age-range."
    )

    age_end = graphene.Field(
        type=graphene.Float,
        description="The end of the age-range."
    )


class TypeLatestDescriptor(graphene.ObjectType):
    """ Graphene type representing a single result of an aggregation operation
        calculating the latest MeSH descriptor in a group of clinical-trial
        studies.
    """

    mesh_term = graphene.Field(
        type=TypeDescriptor,
        description="The MeSH descriptor."
    )

    date = graphene.Date(
        description="The earliest date the descriptor appears in a study.",
    )


class TypeStudiesStats(graphene.ObjectType):

    count_studies_by_country = graphene.List(
        of_type=TypeCountStudiesCountry,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True,
        ),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    count_studies_by_overall_status = graphene.List(
        of_type=TypeCountStudiesOverallStatus,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True,
        ),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    count_studies_by_facility = graphene.List(
        of_type=TypeCountStudiesFacility,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=True,
        ),
        mesh_descriptor_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of MeSH descriptor primary-key IDs as they "
                        "appear in the `mesh.descriptors` table to filter by.",
            required=False,
        ),
        overall_statuses=graphene.Argument(
            type=graphene.List(of_type=TypeEnumOverallStatus),
            description="A list of overall statuses to filter by.",
            required=False,
        ),
        cities=graphene.Argument(
            type=graphene.List(of_type=graphene.String),
            description="A list of cities to filter by.",
            required=False,
        ),
        states=graphene.Argument(
            type=graphene.List(of_type=graphene.String),
            description="A list of states or regions to filter by.",
            required=False,
        ),
        countries=graphene.Argument(
            type=graphene.List(of_type=graphene.String),
            description="A list of countries to filter by.",
            required=False,
        ),
        current_location_longitude=graphene.Argument(
            type=graphene.Float,
            description="The longitude of the current position from which "
                        "only studies on facilities within a "
                        "`distance_max_km` will be allowed.",
            required=False,
        ),
        current_location_latitude=graphene.Argument(
            type=graphene.Float,
            description="The latitude of the current position from which "
                        "only studies on facilities within a "
                        "`distance_max_km` will be allowed.",
            required=False,
        ),
        distance_max_km=graphene.Argument(
            type=graphene.Int,
            description="The maximum distance in kilometers from the current "
                        "location coordinates within which study facilities "
                        "will be allowed.",
            required=False,
        ),
        order_by=graphene.Argument(
            type=graphene.String,
            description="The field to order the returned entries by.",
            required=False,
        ),
        order=graphene.Argument(
            type=TypeEnumOrder,
            description="The order (ascending or descending) in which the "
                        "returned entries will be ordered.",
            required=False,
        ),
        offset=graphene.Argument(
            type=graphene.Int,
            description="The number of entries to skip when paginating.",
            required=False,
        ),
        limit=graphene.Argument(
            type=graphene.Int,
            description="The number of entries to return when paginating.",
            required=False,
        ),
    )

    count_studies_by_facility_descriptor = graphene.List(
        of_type=TypeCountStudiesFacilityDescriptor,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=True,
        ),
        facility_canonical_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=False,
        ),
        mesh_term_type=graphene.Argument(type=TypeEnumMeshTerm, required=False),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    count_studies_by_descriptor = graphene.List(
        of_type=TypeCountStudiesDescriptor,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=True,
        ),
        mesh_term_type=graphene.Argument(type=TypeEnumMeshTerm, required=False),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    get_unique_cities = graphene.List(
        of_type=graphene.String,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=True,
        ),
    )

    get_unique_states = graphene.List(
        of_type=graphene.String,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=True,
        ),
    )

    get_unique_countries = graphene.List(
        of_type=graphene.String,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=True,
        ),
    )

    get_date_range = graphene.Field(
        type=TypeDateRange,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=False,
        ),
        description=("Retrieves the start-date date-range of the provided "
                     "studies.")
    )

    get_age_range = graphene.Field(
        type=TypeAgeRange,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=False,
        ),
        description="Retrieves the patient eligiblity age-range of the "
                    "provided studies in seconds.",
    )

    get_latest_descriptors = graphene.List(
        of_type=TypeLatestDescriptor,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=True,
        ),
        mesh_term_type=graphene.Argument(
            type=TypeEnumMeshTerm,
            description="The type of MeSH descriptor the operation will be"
                        "limited to.",
            required=False,
        ),
        limit=graphene.Argument(
            type=graphene.Int,
            description="The number of results to return.",
            required=False,
        ),
        description="Retrieves the latest MeSH descriptors applied to a list of"
                    "clinical-trial studies.",
    )

    get_unique_descriptors = graphene.List(
        of_type=TypeDescriptor,
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description="A list of clinical-trial study PK IDs to perform the"
                        "operation within.",
            required=True,
        ),
        mesh_term_type=graphene.Argument(
            type=TypeEnumMeshTerm,
            description="The type of MeSH descriptor the operation will be"
                        "limited to.",
            required=False,
        ),
        description="Retrieves the unique MeSH descriptors applied to a list of"
                    "clinical-trial studies.",
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
        func_count_studies = sqlalchemy_func.count(
            sqlalchemy_func.distinct(ModelStudy.study_id),
        )

        # Query out the count of studies by country.
        query = session.query(
            ModelFacilityCanonical.country,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.join(ModelStudy.facilities_canonical)

        if study_ids:
            query = query.filter(ModelStudy.study_id.in_(study_ids))

        # Group by study country.
        query = query.group_by(ModelFacilityCanonical.country)
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
        func_count_studies = sqlalchemy_func.count(
            sqlalchemy_func.distinct(ModelStudy.study_id),
        )

        # Query out the count of studies by overall-status.
        query = session.query(
            ModelStudy.overall_status,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query

        if study_ids:
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
        mesh_descriptor_ids: List[int] = None,
        overall_statuses: Optional[List[EnumOverallStatus]] = None,
        cities: Optional[List[str]] = None,
        states: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        current_location_longitude: Optional[float] = None,
        current_location_latitude: Optional[float] = None,
        distance_max_km: Optional[int] = None,
        order_by: Optional[str] = None,
        order: Optional[TypeEnumOrder] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[TypeCountStudiesFacility]:
        """ Creates a list of `TypeCountStudiesFacility` objects with the number
            of clinical-trial studies per canonical facility.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.
            mesh_descriptor_ids (List[int] = None): A list of MeSH descriptor
                primary-key IDs as they appear in the `mesh.descriptors` table
                to filter by.
            overall_statuses (Optional[List[EnumOverallStatus]] = None): A list
                of overall statuses to filter by.
            cities (Optional[List[str]] = None): A list of cities to filter by.
            states (Optional[List[str]] = None): A list of states or regions to
                filter by.
            countries (Optional[List[str]] = None): A list of countries to
                filter by.
            current_location_longitude (Optional[float] = None): The longitude
                of the current position from which only studies on facilities
                within a `distance_max_km` will be allowed.
            current_location_latitude (Optional[float] = None): The latitude
                of the current position from which only studies on facilities
                within a `distance_max_km` will be allowed.
            distance_max_km (Optional[int] = None): The maximum distance in
                kilometers from the current location coordinates within which
                study facilities will be allowed.
            order_by (Optional[str] = None): The field to order the returned
                entries by.
            order (Optional[TypeEnumOrder] = None): The order (ascending or
                descending) in which the returned entries will be ordered.
            offset (Optional[int] = None): The number of entries to skip when
                paginating.
            limit (Optional[int] = None): The number of entries to return when
                paginating.

        Returns:
             list[TypeCountStudiesFacility]: The list of
                `TypeCountStudiesFacility` objects with the results of the
                aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(studies.study_id)` function.
        func_count_studies = sqlalchemy_func.count(
            sqlalchemy_func.distinct(ModelStudy.study_id),
        )

        # Query out the count of studies by facility.
        query = session.query(
            ModelFacilityCanonical,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.join(ModelStudy.facilities_canonical)

        if study_ids:
            query = query.filter(ModelStudy.study_id.in_(study_ids))

        # Group by study facility.
        query = query.group_by(ModelFacilityCanonical.facility_canonical_id)
        # Order by the number of studies.
        query = query.order_by(func_count_studies.desc())

        # Extract the fields requested in the GraphQL query.
        fields = extract_requested_fields(
            info=info,
            fields=info.field_asts,
            do_convert_to_snake_case=True,
        )["count_studies_by_facility"]["facility_canonical"]

        # Limit query to `FacilityCanonical` fields requested in the GraphQL
        # query.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelFacilityCanonical,
            fields={"facility": fields},
        )

        # Limit studies to those with one of the defined IDs.
        query = query.filter(ModelStudy.study_id.in_(study_ids))

        # Apply an overall-status filter if any are defined.
        if overall_statuses:
            _members = [
                EnumOverallStatus.get_member(value=str(_status))
                for _status in overall_statuses
            ]
            query = query.filter(ModelStudy.overall_status.in_(_members))

        # Join to the study facility locations and apply filters if any such
        # filters are defined.
        if cities or states or countries:
            query = query.join(ModelStudy.facilities_canonical)
            if cities:
                query = query.filter(
                    ModelFacilityCanonical.locality.in_(cities),
                )
            if states:
                query = query.filter(
                    ModelFacilityCanonical.administrative_area_level_1.in_(
                        states,
                    )
                )
            if countries:
                query = query.filter(
                    ModelFacilityCanonical.country.in_(countries),
                )

        if (
            current_location_longitude and
            current_location_latitude and
            distance_max_km
        ):
            query = query.join(ModelStudy.facilities_canonical)
            # Convert distance to meters.
            distance_max_m = distance_max_km * 1000
            # Define the function to calculate the distance between the given
            # coordinates and study facilities.
            func_distance = sqlalchemy_func.ST_Distance_Sphere(
                sqlalchemy_func.ST_GeomFromText(
                    "POINT({} {})".format(
                        current_location_longitude,
                        current_location_latitude
                    ),
                ),
                ModelFacilityCanonical.coordinates,
            )

            # If a maximum age is defined then only include studies without a
            # facility within the distance from the defined coordinates.
            query = query.filter(func_distance <= distance_max_m)

        # Join to the study descriptors and apply filters if any such filters
        # are defined.
        if mesh_descriptor_ids:
            query = query.join(ModelStudy.descriptors)
            query = query.filter(
                ModelStudyDescriptor.descriptor_id.in_(mesh_descriptor_ids)
            )

        # Apply order (if defined).
        if order_by:
            # Convert the order-by field to snake-case. This allows for fields
            # to be defined in camel-case but won't error-out if the fields are
            # already in snake-case.
            order_by = to_snake_case(order_by)

            if order and order == TypeEnumOrder.DESC.value:
                query = query.order_by(
                    getattr(ModelFacilityCanonical, order_by).desc(),
                )
            else:
                query = query.order_by(
                    getattr(ModelFacilityCanonical, order_by).asc(),
                )

        # Apply offset (if defined).
        if offset:
            query = query.offset(offset=offset)

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        results = query.all()

        # Wrap the results of the aggregation in `TypeCountStudiesFacility`
        # objects.
        objs = [
            TypeCountStudiesFacility(
                facility_canonical=result[0],
                count_studies=result[1]
            ) for result in results
        ]

        return objs

    @staticmethod
    def resolve_count_studies_by_facility_descriptor(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
        facility_canonical_ids: Optional[List[int]] = None,
        mesh_term_type: Optional[EnumMeshTerm] = None,
        limit: Optional[int] = None,
    ) -> List[TypeCountStudiesFacilityDescriptor]:
        """Creates a list of `TypeCountStudiesFacilityMeshTerm` objects with
        the number of clinical-trial studies per canonical facility and
        mesh-term.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.
            facility_canonical_ids (Optional[List[int]]): A list of
                FacilityCanonical IDs.
            mesh_term_type (Optional[List[int]]): The type of MeSH descriptor
                to filter on.
            limit (Optional[int]): The number of results to return. Defaults to
                `None` in which case all results are returned.

        Returns:
             List[TypeCountStudiesFacilityDescriptor]: The list of
                `TypeCountStudiesFacilityDescriptor` objects with the results of
                the aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(studies.study_id)` function.
        func_count_studies = sqlalchemy_func.count(
            sqlalchemy_func.distinct(ModelStudy.study_id),
        )

        # Query out the count of studies by facility.
        query = session.query(
            ModelFacilityCanonical,
            ModelDescriptor,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.join(
            ModelStudyFacility,
            ModelFacilityCanonical.facility_canonical_id ==
            ModelStudyFacility.facility_canonical_id,
        )
        query = query.join(
            ModelStudy,
            ModelStudyFacility.study_id == ModelStudy.study_id,
        )
        query = query.join(
            ModelStudyDescriptor,
            ModelStudyDescriptor.study_id == ModelStudy.study_id,
        )
        query = query.join(
            ModelDescriptor,
            ModelDescriptor.descriptor_id == ModelStudyDescriptor.descriptor_id,
        )

        if study_ids:
            query = query.filter(ModelStudy.study_id.in_(study_ids))

        if mesh_term_type:
            _member = EnumMeshTerm.get_member(value=str(mesh_term_type))
            query = query.filter(
                ModelStudyDescriptor.study_descriptor_type == _member,
            )

        if facility_canonical_ids:
            query = query.filter(
                ModelFacilityCanonical.facility_canonical_id.in_(
                    facility_canonical_ids,
                )
            )

        # Group by study facility.
        query = query.group_by(
            ModelFacilityCanonical.facility_canonical_id,
            ModelDescriptor.descriptor_id,
        )
        # Order by the number of studies.
        query = query.order_by(func_count_studies.desc())

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        results = query.all()

        # Wrap the results of the aggregation in `TypeCountStudiesFacility`
        # objects.
        objs = [
            TypeCountStudiesFacilityDescriptor(
                facility_canonical=result[0],
                mesh_term=result[1],
                count_studies=result[2]
            ) for result in results
        ]

        return objs

    @staticmethod
    def resolve_count_studies_by_descriptor(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
        mesh_term_type: Optional[EnumMeshTerm] = None,
        limit: Optional[int] = None,
    ) -> List[TypeCountStudiesDescriptor]:
        """Creates a list of `TypeCountStudiesDescriptor` objects with the
            number of clinical-trial studies per descriptor.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.
            mesh_term_type (Optional[List[int]]): The type of MeSH descriptor
                to filter on.
            limit (Optional[int]): The number of results to return. Defaults to
                `None` in which case all results are returned.

        Returns:
             List[TypeCountStudiesFacilityDescriptor]: The list of
                `TypeCountStudiesFacilityDescriptor` objects with the results of
                the aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(studies.study_id)` function.
        func_count_studies = sqlalchemy_func.count(
            sqlalchemy_func.distinct(ModelStudyDescriptor.study_id),
        )

        # Query out the count of studies by facility.
        query = session.query(
            ModelDescriptor,
            func_count_studies,
        )  # type: sqlalchemy.orm.Query
        query = query.join(
            ModelStudyDescriptor,
            ModelDescriptor.descriptor_id == ModelStudyDescriptor.descriptor_id,
        )
        if study_ids:
            query = query.filter(ModelStudyDescriptor.study_id.in_(study_ids))

        if mesh_term_type:
            _member = EnumMeshTerm.get_member(value=str(mesh_term_type))
            query = query.filter(
                ModelStudyDescriptor.study_descriptor_type == _member,
            )

        # Group by study descriptor.
        query = query.group_by(ModelDescriptor.descriptor_id)
        # Order by the number of studies.
        query = query.order_by(func_count_studies.desc())

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        results = query.all()

        # Wrap the results of the aggregation in `TypeCountStudiesDescriptor`
        # objects.
        objs = [
            TypeCountStudiesDescriptor(
                mesh_term=result[0],
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

        # Define the `DISTINCT(facilities_canonical.locality)` function.
        func_unique_cities = sqlalchemy_func.distinct(
            ModelFacilityCanonical.locality
        )

        # Query out the unique cities of the studies.
        query = session.query(func_unique_cities)  # type: sqlalchemy.orm.Query
        query = query.join(ModelStudy.facilities_canonical)

        if study_ids:
            query = query.filter(ModelStudy.study_id.in_(study_ids))

        results = query.all()

        # Unpack the cities out of the results.
        cities = [result[0] for result in results if result[0]]

        return cities

    @staticmethod
    def resolve_get_unique_states(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
    ) -> List[str]:
        """Retrieves a list of unique states out of a list of clinical-trial
        studies.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.

        Returns:
             list[str]: The list of unique states.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the
        # `DISTINCT(facilities_canonical.administrative_area_level_1)` function.
        func_unique_states = sqlalchemy_func.distinct(
            ModelFacilityCanonical.administrative_area_level_1,
        )

        # Query out the unique states of the studies.
        query = session.query(func_unique_states)  # type: sqlalchemy.orm.Query
        query = query.join(ModelStudy.facilities_canonical)

        if study_ids:
            query = query.filter(ModelStudy.study_id.in_(study_ids))

        results = query.all()

        # Unpack the states out of the results.
        states = [result[0] for result in results if result[0]]

        return states

    @staticmethod
    def resolve_get_unique_countries(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
    ) -> List[str]:
        """Retrieves a list of unique countries out of a list of clinical-trial
        studies.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of Study IDs.

        Returns:
             list[str]: The list of unique countries.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `DISTINCT(facilities_canonical.country)` function.
        func_unique_countries = sqlalchemy_func.distinct(
            ModelFacilityCanonical.country,
        )

        # Query out the unique countries of the studies.
        query = session.query(
            func_unique_countries,
        )  # type: sqlalchemy.orm.Query
        query = query.join(ModelStudy.facilities_canonical)

        if study_ids:
            query = query.filter(ModelStudy.study_id.in_(study_ids))

        results = query.all()

        # Unpack the countries out of the results.
        countries = [result[0] for result in results if result[0]]

        return countries

    @staticmethod
    def resolve_get_date_range(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: Optional[List[int]] = None,
    ) -> TypeDateRange:
        """Retrieves the start-date date-range of the provided studies.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (Optional[List[int]] = None): A list of Study IDs.

        Returns:
             TypeDateRange: The study start-date range.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `MIN(studies.start_date)` function.
        func_min_date = sqlalchemy_func.min(ModelStudy.start_date)

        # Define the `MAX(studies.start_date)` function.
        func_max_date = sqlalchemy_func.max(ModelStudy.start_date)

        # Query out the start-date range of the studies.
        query = session.query(
            func_min_date,
            func_max_date,
        )  # type: sqlalchemy.orm.Query

        if study_ids:
            query = query.filter(ModelStudy.study_id.in_(study_ids))

        results = query.all()

        result = TypeDateRange(results[0][0], results[0][1])

        return result

    @staticmethod
    def resolve_get_age_range(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: Optional[List[int]] = None,
    ) -> TypeAgeRange:
        """Retrieves the patient eligiblity age-range of the provided studies in
        seconds.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (Optional[List[int]] = None): A list of Study IDs.

        Returns:
             TypeAgeRange: The study eligiblity age-range.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the function to calculate the minimum elligible age in seconds.
        func_min_age_sec = sqlalchemy_func.min(
            sqlalchemy_func.extract(
                "EPOCH",
                sqlalchemy_func.cast(
                    ModelEligibility.minimum_age,
                    postgresql.INTERVAL,
                ),
            ),
        )

        # Define the function to calculate the maximum elligible age in seconds.
        func_max_age_sec = sqlalchemy_func.max(
            sqlalchemy_func.extract(
                "EPOCH",
                sqlalchemy_func.cast(
                    ModelEligibility.maximum_age,
                    postgresql.INTERVAL,
                ),
            ),
        )

        # Query out the start-date range of the studies.
        query = session.query(
            func_min_age_sec,
            func_max_age_sec,
        )  # type: sqlalchemy.orm.Query
        query = query.join(ModelStudy.eligibility)

        if study_ids:
            query = query.filter(ModelStudy.study_id.in_(study_ids))

        results = query.all()

        result = TypeAgeRange(results[0][0], results[0][1])

        return result

    @staticmethod
    def resolve_get_latest_descriptors(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
        mesh_term_type: Optional[EnumMeshTerm] = None,
        limit: Optional[int] = None,
    ) -> List[TypeLatestDescriptor]:
        """ Creates a list of `TypeLatestDescriptor` objects with the latest
            descriptors.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of clinical-trial study PK IDs to
                perform the operation within.
            mesh_term_type (mesh_term_type: Optional[EnumMeshTerm] = None): The
                type of MeSH descriptor the operation will be limited to.
            limit (limit: Optional[int] = None): The number of results to
                return.

        Returns:
             List[TypeLatestDescriptor]: The list of `TypeLatestDescriptor`
                objects with the results of the aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `MIN(studies.start_date)` function.
        func_min_start_date = sqlalchemy_func.min(ModelStudy.start_date)

        # Query out the MeSH descriptors and the minimum date they appear in.
        query = session.query(
            ModelDescriptor,
            func_min_start_date,
        )  # type: sqlalchemy.orm.Query
        query = query.join(
            ModelStudyDescriptor,
            ModelDescriptor.descriptor_id == ModelStudyDescriptor.descriptor_id,
        )
        query = query.join(
            ModelStudy,
            ModelStudyDescriptor.study_id == ModelStudy.study_id,
        )
        if study_ids:
            query = query.filter(ModelStudyDescriptor.study_id.in_(study_ids))
        query = query.filter(ModelStudy.start_date.isnot(None))

        if mesh_term_type:
            _member = EnumMeshTerm.get_member(value=str(mesh_term_type))
            query = query.filter(
                ModelStudyDescriptor.study_descriptor_type == _member,
            )

        # Group by study descriptor.
        query = query.group_by(ModelDescriptor.descriptor_id)
        # Order by the minimum study date.
        query = query.order_by(func_min_start_date.desc())

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        results = query.all()

        # Wrap the results of the aggregation in `TypeLatestDescriptor` objects.
        objs = [
            TypeLatestDescriptor(
                mesh_term=result[0],
                date=result[1],
            ) for result in results
        ]

        return objs

    @staticmethod
    def resolve_get_unique_descriptors(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
        mesh_term_type: Optional[EnumMeshTerm] = None,
    ) -> List[TypeDescriptor]:
        """ Creates a list of `TypeLatestDescriptor` objects with the latest
            descriptors.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[int]): A list of clinical-trial study PK IDs to
                perform the operation within.
            mesh_term_type (mesh_term_type: Optional[EnumMeshTerm] = None): The
                type of MeSH descriptor the operation will be limited to.

        Returns:
             List[TypeDescriptor]: The list of `TypeDescriptor` objects that
                resulted from the operation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Query out the MeSH descriptors.
        query = session.query(ModelDescriptor)  # type: sqlalchemy.orm.Query
        query = query.join(
            ModelStudyDescriptor,
            ModelDescriptor.descriptor_id == ModelStudyDescriptor.descriptor_id,
        )
        query = query.join(
            ModelStudy,
            ModelStudyDescriptor.study_id == ModelStudy.study_id,
        )
        if study_ids:
            query = query.filter(ModelStudyDescriptor.study_id.in_(study_ids))

        if mesh_term_type:
            _member = EnumMeshTerm.get_member(value=str(mesh_term_type))
            query = query.filter(
                ModelStudyDescriptor.study_descriptor_type == _member,
            )

        objs = query.all()

        return objs
