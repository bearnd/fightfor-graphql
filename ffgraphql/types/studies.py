# coding=utf-8

import datetime
from typing import Union, List, Optional

import sqlalchemy
import sqlalchemy.orm
import graphene
from sqlalchemy.dialects import postgresql
from sqlalchemy import func as sqlalchemy_func
from graphene.utils.str_converters import to_snake_case

from ffgraphql.types.ct_primitives import TypeStudy
from ffgraphql.types.ct_primitives import ModelStudy
from ffgraphql.types.ct_primitives import ModelMeshTerm
from ffgraphql.types.ct_primitives import ModelLocation
from ffgraphql.types.ct_primitives import ModelFacility
from ffgraphql.types.ct_primitives import ModelIntervention
from ffgraphql.types.ct_primitives import ModelEligibility
from ffgraphql.types.ct_primitives import TypeEnumOverallStatus
from ffgraphql.types.ct_primitives import EnumOverallStatus
from ffgraphql.types.ct_primitives import TypeEnumIntervention
from ffgraphql.types.ct_primitives import EnumIntervention
from ffgraphql.types.ct_primitives import TypeEnumPhase
from ffgraphql.types.ct_primitives import EnumPhase
from ffgraphql.types.ct_primitives import TypeEnumStudy
from ffgraphql.types.ct_primitives import EnumStudy
from ffgraphql.types.ct_primitives import TypeEnumOrder
from ffgraphql.types.mt_primitives import ModelTreeNumber
from ffgraphql.types.mt_primitives import ModelDescriptor
from ffgraphql.utils import apply_requested_fields


class TypeStudies(graphene.ObjectType):
    by_nct_id = graphene.List(
        of_type=TypeStudy,
        description="Retrieve clinical-trial studies through their NCT IDs.",
        nct_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.String),
            required=True,
        ),
    )

    by_id = graphene.List(
        of_type=TypeStudy,
        description="Retrieve clinical-trial studies through their IDs.",
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True,
        ),
    )

    search = graphene.List(
        of_type=TypeStudy,
        description=("Retrieve a list of clinical-trial studies matching "
                     "several filters."),
        mesh_descriptor_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True
        ),
        year_beg=graphene.Argument(type=graphene.Int, required=False),
        year_end=graphene.Argument(type=graphene.Int, required=False),
        do_include_children=graphene.Argument(
            type=graphene.Boolean,
            required=False,
            default_value=True,
        )
    )

    filter = graphene.List(
        of_type=TypeStudy,
        description=("Retrieve a list of clinical-trial studies through "
                     "dynamic filtering and sorting."),
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True
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
        intervention_types=graphene.Argument(
            type=graphene.List(of_type=TypeEnumIntervention),
            description="A list of intevention types to filter by.",
            required=False,
        ),
        phases=graphene.Argument(
            type=graphene.List(of_type=TypeEnumPhase),
            description="A list of trial phases to filter by.",
            required=False,
        ),
        study_types=graphene.Argument(
            type=graphene.List(of_type=TypeEnumStudy),
            description="A list of study-types to filter by.",
            required=False,
        ),
        year_beg=graphene.Argument(type=graphene.Int, required=False),
        year_end=graphene.Argument(type=graphene.Int, required=False),
        age_beg_sec=graphene.Argument(type=graphene.Int, required=False),
        age_end_sec=graphene.Argument(type=graphene.Int, required=False),
        order_by=graphene.Argument(type=graphene.String, required=False),
        order=graphene.Argument(type=TypeEnumOrder, required=False),
        offset=graphene.Argument(type=graphene.Int, required=False),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    count = graphene.Int(
        description=("Retrieve a list of clinical-trial studies through "
                     "dynamic filtering and sorting."),
        study_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True
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
        intervention_types=graphene.Argument(
            type=graphene.List(of_type=TypeEnumIntervention),
            description="A list of intevention types to filter by.",
            required=False,
        ),
        phases=graphene.Argument(
            type=graphene.List(of_type=TypeEnumPhase),
            description="A list of trial phases to filter by.",
            required=False,
        ),
        study_types=graphene.Argument(
            type=graphene.List(of_type=TypeEnumStudy),
            description="A list of study-types to filter by.",
            required=False,
        ),
        year_beg=graphene.Argument(type=graphene.Int, required=False),
        year_end=graphene.Argument(type=graphene.Int, required=False),
        age_beg_sec=graphene.Argument(type=graphene.Int, required=False),
        age_end_sec=graphene.Argument(type=graphene.Int, required=False),
    )

    @staticmethod
    def resolve_by_nct_id(
        args: dict,
        info: graphene.ResolveInfo,
        nct_ids: List[str],
    ) -> List[ModelStudy]:
        """Retrieves `ModelStudy` record objects through their NCT IDs.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            nct_ids (List[str]): The NCT IDs for which `ModelStudy` record
                objects will be retrieved.

        Returns:
             List[StudyModel]: The retrieved `ModelStudy` record objects or an
                empty list if no matches were found.
        """

        # Retrieve the query on `ModelStudy`.
        query = TypeStudy.get_query(
            info=info,
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `ModelStudy` records matching any of the `nct_ids`.
        query = query.filter(ModelStudy.nct_id.in_(nct_ids))

        # Limit query to fields requested in the GraphQL query adding
        # `load_only` and `joinedload` options as required.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelStudy,
        )

        objs = query.all()

        return objs

    @staticmethod
    def resolve_by_id(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
    ) -> List[ModelStudy]:
        """Retrieves `ModelStudy` record objects through their IDs.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            study_ids (List[str]): The IDs for which `ModelStudy` record
                objects will be retrieved.

        Returns:
             List[StudyModel]: The retrieved `ModelStudy` record objects or an
                empty list if no matches were found.
        """

        # Retrieve the query on `ModelStudy`.
        query = TypeStudy.get_query(
            info=info,
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `ModelStudy` records matching any of the `study_ids`.
        query = query.filter(ModelStudy.study_id.in_(study_ids))

        # Limit query to fields requested in the GraphQL query adding
        # `load_only` and `joinedload` options as required.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelStudy,
        )

        objs = query.all()

        return objs

    @staticmethod
    def _apply_query_filters(
        query: sqlalchemy.orm.query.Query,
        study_ids: List[int],
        overall_statuses: Optional[List[EnumOverallStatus]] = None,
        cities: Optional[List[str]] = None,
        states: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        intervention_types: Optional[List[EnumIntervention]] = None,
        phases: Optional[List[EnumPhase]] = None,
        study_types: Optional[List[EnumStudy]] = None,
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
        age_beg_sec: Union[int, None] = None,
        age_end_sec: Union[int, None] = None,
    ):

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
            query = query.join(ModelStudy.locations)
            query = query.join(ModelLocation.facility)
            if cities:
                query = query.filter(ModelFacility.city.in_(cities))
            if states:
                query = query.filter(ModelFacility.state.in_(states))
            if countries:
                query = query.filter(ModelFacility.country.in_(countries))

        # Join to the study interventions and apply filters if any such filters
        # are defined.
        if intervention_types:
            _members = [
                EnumIntervention.get_member(value=str(_status))
                for _status in intervention_types
            ]
            query = query.join(ModelStudy.interventions)
            query = query.filter(
                ModelIntervention.intervention_type.in_(_members)
            )

        # Apply an phase filter if any are defined.
        if phases:
            _members = [
                EnumPhase.get_member(value=str(_status))
                for _status in phases
            ]
            query = query.filter(ModelStudy.phase.in_(_members))

        # Apply an study-type filter if any are defined.
        if study_types:
            _members = [
                EnumStudy.get_member(value=str(_status))
                for _status in study_types
            ]
            query = query.filter(ModelStudy.study_type.in_(_members))

        # Filter studies the year of their start-date.
        if year_beg:
            query = query.filter(
                ModelStudy.start_date >= datetime.date(year_beg, 1, 1)
            )
        if year_end:
            query = query.filter(
                ModelStudy.start_date <= datetime.date(year_end, 12, 31)
            )

        # Filter studies by the minimum and maximum eligibility age.
        if age_beg_sec or age_end_sec:
            query = query.join(ModelStudy.eligibility)

            # Define the function to convert the minimum eligible age of each
            # study to seconds.
            func_age_beg_sec = sqlalchemy_func.extract(
                "EPOCH",
                sqlalchemy_func.cast(
                    ModelEligibility.minimum_age,
                    postgresql.INTERVAL,
                ),
            )

            # Define the function to convert the maximum eligible age of each
            # study to seconds.
            func_age_end_sec = sqlalchemy_func.extract(
                "EPOCH",
                sqlalchemy_func.cast(
                    ModelEligibility.maximum_age,
                    postgresql.INTERVAL,
                ),
            )

            # If an minimum age is defined then only include studies without a
            # minimum eligible age or a minimum age greater than or equal to the
            # defined one.
            if age_beg_sec:
                query = query.filter(
                    sqlalchemy.or_(
                        func_age_beg_sec.is_(None),
                        func_age_beg_sec >= age_beg_sec,
                    ),
                )

            # If an maximum age is defined then only include studies without a
            # maximum eligible age or a maximum age less than or equal to the
            # defined one.
            if age_end_sec:
                query = query.filter(
                    sqlalchemy.or_(
                        func_age_end_sec.is_(None),
                        func_age_end_sec <= age_end_sec,
                    ),
                )

        return query

    @staticmethod
    def resolve_search(
        args: dict,
        info: graphene.ResolveInfo,
        mesh_descriptor_ids: Union[List[int]],
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
        do_include_children: Union[bool, None] = True,
    ) -> List[ModelStudy]:
        """Retrieves a list of `ModelStudy` objects matching several optional
        filters.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            mesh_descriptor_ids (List[int]): A list of MeSH descriptor IDs of
                the descriptors tagged against the study.
            year_beg (int, optional): The minimum year the start date of a
                matched `ModelStudy` may have.
            year_end (int, optional): The maximum year the start date of a
                matched `ModelStudy` may have.
            do_include_children (bool, optional): Whether to search for and
                include in the search the children MeSH descriptors of the
                provided descriptors.

        Returns:
             List[StudyModel]: The list of matched `ModelStudy` objects or an
                empty list if no match was found.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # If the search is to account for the provided descriptors and their
        # children the find all the children descriptor names. Otherwise only
        # use the provided ones.
        if do_include_children:
            # Retrieve all tree-numbers for the specified MeSH descriptors.
            query_tns = session.query(ModelTreeNumber.tree_number)
            query_tns = query_tns.join(ModelTreeNumber.descriptors)
            query_tns = query_tns.filter(
                ModelDescriptor.descriptor_id.in_(mesh_descriptor_ids),
            )
            # Retrieve the tree-numbers and get them out of their encompassing
            # tuple.
            tree_numbers = [tn[0] for tn in query_tns.all()]

            # If no tree-numbers have been found return an empty list.
            if not tree_numbers:
                return []

            # Find all names of the descriptors and their children for the found
            # tree-numbers.
            query_descs = session.query(ModelDescriptor.name)
            query_descs = query_descs.join(ModelDescriptor.tree_numbers)
            query_descs = query_descs.filter(
                ModelTreeNumber.tree_number.like(
                    sqlalchemy.any_(postgresql.array(
                        tuple(["{}%".format(tn) for tn in tree_numbers])
                    ))
                )
            )
        else:
            # Find the names of the descriptors defined under
            # `mesh_descriptor_ids`.
            query_descs = session.query(ModelDescriptor.name)
            query_descs = query_descs.filter(
                ModelDescriptor.descriptor_id.in_(mesh_descriptor_ids)
            )
        # Retrieve the descriptor names, get them out of their encompassing
        # tuples, and unique them.
        descriptor_names = list(set([d[0] for d in query_descs.all()]))

        # If no descriptor-names have been found return an empty list.
        if not descriptor_names:
            return []

        # Find all clinical-trial studies associated with the MeSH descriptor
        # found prior.
        query = session.query(ModelStudy)

        # Filter studies by associated mesh-descriptors.
        query = query.join(ModelStudy.mesh_terms)
        query = query.filter(ModelMeshTerm.term.in_(descriptor_names))

        # Filter studies the year of their start-date.
        if year_beg:
            query = query.filter(
                ModelStudy.start_date >= datetime.date(year_beg, 1, 1)
            )
        if year_end:
            query = query.filter(
                ModelStudy.start_date <= datetime.date(year_end, 12, 31)
            )

        # Limit query to fields requested in the GraphQL query.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelStudy,
        )

        objs = query.all()

        return objs

    @staticmethod
    def resolve_filter(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
        overall_statuses: Optional[List[EnumOverallStatus]] = None,
        cities: Optional[List[str]] = None,
        states: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        intervention_types: Optional[List[EnumIntervention]] = None,
        phases: Optional[List[EnumPhase]] = None,
        study_types: Optional[List[EnumStudy]] = None,
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
        age_beg_sec: Union[int, None] = None,
        age_end_sec: Union[int, None] = None,
        order_by: Optional[str] = None,
        order: Optional[TypeEnumOrder] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[ModelStudy]:

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        query = session.query(ModelStudy)  # type: sqlalchemy.orm.query.Query

        # Limit query to fields requested in the GraphQL query adding
        # `load_only` and `joinedload` options as required.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelStudy,
        )

        # Apply the different optional filters to the query.
        query = TypeStudies._apply_query_filters(
            query=query,
            study_ids=study_ids,
            overall_statuses=overall_statuses,
            cities=cities,
            states=states,
            countries=countries,
            intervention_types=intervention_types,
            phases=phases,
            study_types=study_types,
            year_beg=year_beg,
            year_end=year_end,
            age_beg_sec=age_beg_sec,
            age_end_sec=age_end_sec,
        )

        # Apply order (if defined).
        if order_by:
            # Convert the order-by field to snake-case. This allows for fields
            # to be defined in camel-case but won't error-out if the fields are
            # already in snake-case.
            order_by = to_snake_case(order_by)
            
            if order and order == TypeEnumOrder.DESC.value:
                query = query.order_by(getattr(ModelStudy, order_by).desc())
            else:
                query = query.order_by(getattr(ModelStudy, order_by).asc())

        # Apply offset (if defined).
        if offset:
            query = query.offset(offset=offset)

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        objs = query.all()

        return objs

    @staticmethod
    def resolve_count(
        args: dict,
        info: graphene.ResolveInfo,
        study_ids: List[int],
        overall_statuses: Optional[List[TypeEnumOverallStatus]] = None,
        cities: Optional[List[str]] = None,
        states: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        intervention_types: Optional[List[TypeEnumIntervention]] = None,
        phases: Optional[List[TypeEnumPhase]] = None,
        study_types: Optional[List[TypeEnumStudy]] = None,
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
        age_beg_sec: Union[int, None] = None,
        age_end_sec: Union[int, None] = None,
    ) -> int:

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(studies.study_id)` function.
        func_count_studies = sqlalchemy_func.count(ModelStudy.study_id)

        query = session.query(
            func_count_studies,
        )  # type: sqlalchemy.orm.query.Query

        # Apply the different optional filters to the query.
        query = TypeStudies._apply_query_filters(
            query=query,
            study_ids=study_ids,
            overall_statuses=overall_statuses,
            cities=cities,
            states=states,
            countries=countries,
            intervention_types=intervention_types,
            phases=phases,
            study_types=study_types,
            year_beg=year_beg,
            year_end=year_end,
            age_beg_sec=age_beg_sec,
            age_end_sec=age_end_sec,
        )

        count = 0
        result = query.one_or_none()
        if result:
            count = result[0]

        return count
