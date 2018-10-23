# coding=utf-8

import uuid

import sqlalchemy
import sqlalchemy.orm
import graphene
import graphql

from ffgraphql.types.app_primitives import TypeSearch
from ffgraphql.types.app_primitives import ModelSearch
from ffgraphql.utils import apply_requested_fields
from ffgraphql.utils import check_auth
from ffgraphql.mutations.utils import clean_auth0_user_id


class TypeSearches(graphene.ObjectType):

    by_search_uuid = graphene.Field(
        type=TypeSearch,
        description="Retrieve a user search through its UUID.",
        auth0_user_id=graphene.Argument(
            type=graphene.String,
            required=True,
            description="The user Auth0 ID."
        ),
        search_uuid=graphene.Argument(
            type=graphene.UUID,
            required=True,
            description="The search UUID."
        )
    )

    @staticmethod
    def resolve_by_search_uuid(
        args: dict,
        info: graphene.ResolveInfo,
        auth0_user_id: str,
        search_uuid: str,
    ) -> ModelSearch:
        """ Retrieves a `ModelUser` record object through its Auth0 IDs.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            auth0_user_id (str): The Auth0 ID of the user to which the search
                belongs.
            search_uuid (uuid.UUID): The search UUID for which the
                `ModelSearch` record object will be retrieved.

        Returns:
             ModelSearch: The retrieved `ModelSearch` record object or `None`
                if no matches were found.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(auth0_user_id=str(auth0_user_id))

        # Check that the requesting user is authorized to retrieve the user with
        # the given Auth0 ID.
        check_auth(info=info, auth0_user_id=auth0_user_id)

        # Retrieve the query on `ModelSearch`.
        query = TypeSearch.get_query(
            info=info,
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `ModelSearch` record matching the `search_uuid`.
        query = query.filter(ModelSearch.search_uuid == search_uuid)

        # Limit query to fields requested in the GraphQL query adding
        # `load_only` and `joinedload` options as required.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelSearch,
        )

        obj = query.one_or_none()

        # Raise an exception if the requested search could not be found.
        if not obj:
            msg = "Search with UUID '{}' could not be found."
            msg_fmt = msg.format(search_uuid)
            raise graphql.GraphQLError(message=msg_fmt)

        return obj
