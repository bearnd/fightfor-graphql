# coding=utf-8

import datetime
from typing import Union, List, Optional

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.dialects import postgresql
import graphene

from ffgraphql.types.ct_primitives import TypeStudy
from ffgraphql.types.ct_primitives import ModelStudy
from ffgraphql.types.ct_primitives import ModelMeshTerm
from ffgraphql.types.ct_primitives import ModelLocation
from ffgraphql.types.ct_primitives import ModelFacility
from ffgraphql.types.ct_primitives import ModelTreeNumber
from ffgraphql.types.ct_primitives import ModelDescriptor
from ffgraphql.types.ct_primitives import ModelIntervention
from ffgraphql.types.ct_primitives import EnumOverallStatus
from ffgraphql.types.ct_primitives import EnumIntervention
from ffgraphql.types.ct_primitives import EnumPhase
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
            type=graphene.List(
                of_type=graphene.Enum.from_enum(EnumOverallStatus),
            ),
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
            type=graphene.List(
                of_type=graphene.Enum.from_enum(EnumIntervention),
            ),
            description="A list of intevention types to filter by.",
            required=False,
        ),
        phases=graphene.Argument(
            type=graphene.List(
                of_type=graphene.Enum.from_enum(EnumPhase),
            ),
            description="A list of trial phases to filter by.",
            required=False,
        ),
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

        # Limit query to fields requested in the GraphQL query.
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

        # Limit query to fields requested in the GraphQL query.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelStudy,
        )

        objs = query.all()

        return objs

    @staticmethod
    def resolve_search(
        args: dict,
        info: graphene.ResolveInfo,
        mesh_descriptor_ids: Union[List[int]],
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
        do_include_children: Union[bool, None] = True,
    ):
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
             list[StudyModel]: The list of matched `ModelStudy` objects or an
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
        # order_by: Optional[List[str]] = None,
        # order: Optional[List[OrderType]] = None,
    ):

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        query = session.query(ModelStudy)

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

        objs = query.all()

        return objs
