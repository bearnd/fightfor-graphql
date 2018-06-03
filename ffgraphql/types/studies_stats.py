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
        mesh_descriptors=graphene.Argument(
            type=graphene.List(of_type=graphene.String),
            required=False
        ),
        year_beg=graphene.Argument(type=graphene.Int, required=False),
        year_end=graphene.Argument(type=graphene.Int, required=False),
    )

    count_studies_by_overall_status = graphene.List(
        of_type=TypeCountStudiesOverallStatus,
        mesh_descriptors=graphene.Argument(
            type=graphene.List(of_type=graphene.String),
            required=False
        ),
        year_beg=graphene.Argument(type=graphene.Int, required=False),
        year_end=graphene.Argument(type=graphene.Int, required=False),
    )

    @staticmethod
    def resolve_count_studies_by_country(
        args: dict,
        info: graphene.ResolveInfo,
        mesh_descriptors: Union[List[str], None] = None,
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
    ) -> List[TypeCountStudiesCountry]:
        """Creates a list of `TypeCountStudiesCountry` objects with the number
        of clinical-trial studies per country.

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
        mesh_descriptors: Union[List[str], None] = None,
        year_beg: Union[int, None] = None,
        year_end: Union[int, None] = None,
    ) -> List[TypeCountStudiesOverallStatus]:
        """Creates a list of `TypeCountStudiesOverallStatus` objects with the
        number of clinical-trial studies per overall-status.

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
