# coding=utf-8

from typing import List

import sqlalchemy
import sqlalchemy.orm
import graphene
import graphql

from ffgraphql.types.app_primitives import TypeUser
from ffgraphql.types.app_primitives import ModelUser
from ffgraphql.utils import apply_requested_fields
from ffgraphql.utils import check_auth
from ffgraphql.mutations.utils import clean_auth0_user_id


class TypeUsers(graphene.ObjectType):

    by_auth0_id = graphene.Field(
        type=TypeUser,
        description="Retrieve an application user through their Auth0 ID.",
        auth0_user_id=graphene.Argument(
            type=graphene.String,
            required=True,
            description="The user Auth0 ID."
        )
    )

    @staticmethod
    def resolve_by_auth0_id(
        args: dict,
        info: graphene.ResolveInfo,
        auth0_user_id: str,
    ) -> List[ModelUser]:
        """ Retrieves a `ModelUser` record object through its Auth0 IDs.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            auth0_user_id (str): The Auth0 ID for which the `ModelUser` record
                object will be retrieved.

        Returns:
             ModelUser: The retrieved `ModelUser` record object or `None` if no
                matches were found.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(auth0_user_id=str(auth0_user_id))

        # Check that the requesting user is authorized to retrieve the user with
        # the given Auth0 ID.
        check_auth(info=info, auth0_user_id=auth0_user_id)

        # Retrieve the query on `ModelUser`.
        query = TypeUser.get_query(
            info=info,
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `ModelUser` record matching the `auth0_user_id`.
        query = query.filter(ModelUser.auth0_user_id == auth0_user_id)

        # Limit query to fields requested in the GraphQL query adding
        # `load_only` and `joinedload` options as required.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelUser,
        )

        obj = query.one_or_none()

        # Raise an exception if the requested user could not be found.
        if not obj:
            msg = "User with Auth0 ID '{}' could not be found."
            msg_fmt = msg.format(auth0_user_id)
            raise graphql.GraphQLError(message=msg_fmt)

        return obj
