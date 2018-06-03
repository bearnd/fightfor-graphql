# coding=utf-8

import hashlib
import datetime
from typing import Union, List

import sqlalchemy.orm
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from fform.orm_ct import Study as StudyModel
from fform.orm_ct import MeshTerm as MeshTermModel


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
        mesh_descriptors=graphene.Argument(
            type=graphene.List(of_type=graphene.String),
            required=False
        ),
        year_beg=graphene.Argument(type=graphene.Int, required=False),
        year_end=graphene.Argument(type=graphene.Int, required=False),
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
        mesh_descriptors: Union[List[str], None] = None,
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
    ):
        """Retrieves a list of `StudyModel` objects matching several optional
        filters.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            mesh_descriptors (list[str], optional): A list of MeSH descriptor
                names tagged against the study.
            year_beg (int, optional): The minimum year the start date of a
                matched `StudyModel` may have.
            year_end (int, optional): The maximum year the start date of a
                matched `StudyModel` may have.

        Returns:
             list[StudyModel]: The list of matched `StudyModel` objects or an
                empty list if no match was found.
        """

        query = StudyType.get_query(info=info)

        # Filter studies by associated mesh-descriptors.
        if mesh_descriptors:
            # Calculate the MD5 hashes for the defined descriptors.
            mesh_descriptor_md5s = [
                hashlib.md5(descriptor.encode("utf-8")).digest()
                for descriptor in mesh_descriptors
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

        objs = query.all()

        return objs
