# coding=utf-8

import hashlib
import datetime
from typing import Union, List

import sqlalchemy.orm
from sqlalchemy.dialects import postgresql
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from fform.orm_ct import Study as StudyModel
from fform.orm_ct import MeshTerm as MeshTermModel
from fform.orm_mt import Descriptor as DescriptorModel
from fform.orm_mt import TreeNumber as TreeNumberModel

from ffgraphql.utils import apply_requested_fields


class StudyType(SQLAlchemyObjectType):
    class Meta:
        model = StudyModel


class StudiesType(graphene.ObjectType):
    by_nct_id = graphene.Field(
        type=StudyType,
        description="Retrieve a clinical-trial study through its NCT ID.",
        nct_id=graphene.Argument(type=graphene.String, required=True),
    )

    search = graphene.List(
        of_type=StudyType,
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

    @staticmethod
    def resolve_by_nct_id(
        args: dict,
        info: graphene.ResolveInfo,
        nct_id: str
    ) -> StudyModel:
        """Retrieves a `StudyModel` object through its NCT ID.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            nct_id (str): The NCT ID of the `StudyModel` to retrieve.

        Returns:
             StudyModel: The retrieved `StudyModel` object or `None`
                if no match was not found.
        """

        # Retrieve the query on `StudyModel`.
        query = StudyType.get_query(
            info=info,
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `StudyModel` record matching `nct_id`.
        query = query.filter(StudyModel.nct_id == nct_id)

        obj = query.first()

        return obj

    @staticmethod
    def resolve_search(
        args: dict,
        info: graphene.ResolveInfo,
        mesh_descriptor_ids: Union[List[int]],
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
        do_include_children: Union[bool, None] = True,
    ):
        """Retrieves a list of `StudyModel` objects matching several optional
        filters.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            mesh_descriptor_ids (List[int]): A list of MeSH descriptor IDs of
                the descriptors tagged against the study.
            year_beg (int, optional): The minimum year the start date of a
                matched `StudyModel` may have.
            year_end (int, optional): The maximum year the start date of a
                matched `StudyModel` may have.
            do_include_children (bool, optional): Whether to search for and
                include in the search the children MeSH descriptors of the
                provided descriptors.

        Returns:
             list[StudyModel]: The list of matched `StudyModel` objects or an
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
            query_tns = session.query(TreeNumberModel.tree_number)
            query_tns = query_tns.join(TreeNumberModel.descriptors)
            query_tns = query_tns.filter(
                DescriptorModel.descriptor_id.in_(mesh_descriptor_ids),
            )
            # Retrieve the tree-numbers and get them out of their encompassing
            # tuple.
            tree_numbers = [tn[0] for tn in query_tns.all()]

            # If no tree-numbers have been found return an empty list.
            if not tree_numbers:
                return []

            # Find all names of the descriptors and their children for the found
            # tree-numbers.
            query_descs = session.query(DescriptorModel.name)
            query_descs = query_descs.join(DescriptorModel.tree_numbers)
            query_descs = query_descs.filter(
                TreeNumberModel.tree_number.like(
                    sqlalchemy.any_(postgresql.array(
                        tuple(["{}%".format(tn) for tn in tree_numbers])
                    ))
                )
            )
        else:
            # Find the names of the descriptors defined under
            # `mesh_descriptor_ids`.
            query_descs = session.query(DescriptorModel.name)
            query_descs = query_descs.filter(
                DescriptorModel.descriptor_id.in_(mesh_descriptor_ids)
            )
        # Retrieve the descriptor names, get them out of their encompassing
        # tuples, and unique them.
        descriptor_names = list(set([d[0] for d in query_descs.all()]))

        # If no descriptor-names have been found return an empty list.
        if not descriptor_names:
            return []

        # Find all clinical-trial studies associated with the MeSH descriptor
        # found prior.
        query = session.query(StudyModel)

        # Filter studies by associated mesh-descriptors.
        # Calculate the MD5 hashes for the defined descriptors.
        mesh_descriptor_md5s = [
            hashlib.md5(descriptor_name.encode("utf-8")).digest()
            for descriptor_name in descriptor_names
        ]
        # Filter studies by descriptor MD5 hashes.
        query = query.join(StudyModel.mesh_terms)
        query = query.filter(MeshTermModel.md5.in_(mesh_descriptor_md5s))

        # Filter studies the year of their start-date.
        if year_beg:
            query = query.filter(
                StudyModel.start_date >= datetime.date(year_beg, 1, 1)
            )
        if year_end:
            query = query.filter(
                StudyModel.start_date <= datetime.date(year_end, 12, 31)
            )

        # Limit query to fields requested in the GraphQL query.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=StudyModel,
        )

        objs = query.all()

        return objs
