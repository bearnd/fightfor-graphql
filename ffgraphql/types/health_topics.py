# -*- coding: utf-8 -*-

from typing import List

import sqlalchemy
import sqlalchemy.orm
import graphene

from ffgraphql.types.mp_primitives import (
    TypeHealthTopic,
    TypeHealthTopicGroup,
    TypeBodyPart,
)
from ffgraphql.types.mp_primitives import (
    ModelHealthTopic,
    ModelHealthTopicGroup,
    ModelHealthTopicGroupClass,
    ModelBodyPart,
)
from ffgraphql.utils import apply_requested_fields


class TypeHealthTopics(graphene.ObjectType):
    by_body_part_name = graphene.List(
        of_type=TypeHealthTopic,
        description=(
            "Retrieve MedlinePlus health-topics by the name of the body-part "
            "they belong to."
        ),
        body_part_name=graphene.Argument(
            type=graphene.String,
            required=True,
            description=(
                "The name of the body-part to retrieve health-topics for."
            ),
        ),
    )

    by_group_name = graphene.List(
        of_type=TypeHealthTopic,
        description=(
            "Retrieve MedlinePlus health-topics by the name of the group they "
            "belong to."
        ),
        group_name=graphene.Argument(
            type=graphene.String,
            required=True,
            description=(
                "The name of the health-topic group to retrieve health-topics "
                "for."
            ),
        ),
    )

    @staticmethod
    def resolve_by_body_part_name(
        args: dict, info: graphene.ResolveInfo, body_part_name: str
    ) -> List[ModelHealthTopic]:
        """ Retrieves `ModelHealthTopic` record objects through their body-part
            name.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            body_part_name (str): The name of the body-part to retrieve
                health-topics for.

        Returns:
             List[ModelHealthTopic]: The retrieved `ModelHealthTopic` record
                objects or an empty list if no matches were found.
        """

        # Retrieve the query on `ModelHealthTopic`.
        query = TypeHealthTopic.get_query(
            info=info
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `ModelHealthTopic` records matching the given
        # body-part.
        query = query.join(ModelHealthTopic.body_parts)
        query = query.filter(ModelBodyPart.name == body_part_name)

        # Limit query to fields requested in the GraphQL query adding
        # `load_only` and `joinedload` options as required.
        query = apply_requested_fields(
            info=info, query=query, orm_class=ModelHealthTopic
        )

        objs = query.all()

        return objs

    @staticmethod
    def resolve_by_group_name(
        args: dict, info: graphene.ResolveInfo, group_name: str
    ) -> List[ModelHealthTopic]:
        """ Retrieves `ModelHealthTopic` record objects through their group
            name.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            group_name (str): The name of the health-topic group to retrieve
                health-topics for.

        Returns:
             List[ModelHealthTopic]: The retrieved `ModelHealthTopic` record
                objects or an empty list if no matches were found.
        """

        # Retrieve the query on `ModelHealthTopic`.
        query = TypeHealthTopic.get_query(
            info=info
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `ModelHealthTopic` records matching the given
        # group.
        query = query.join(ModelHealthTopic.health_topic_groups)
        query = query.filter(ModelHealthTopicGroup.name == group_name)

        # Limit query to fields requested in the GraphQL query adding
        # `load_only` and `joinedload` options as required.
        query = apply_requested_fields(
            info=info, query=query, orm_class=ModelHealthTopic
        )

        objs = query.all()

        return objs

