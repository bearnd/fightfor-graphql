# coding=utf-8

import uuid
from typing import Dict, List

import graphql
import graphene
import sqlalchemy.orm
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.engine.result import ResultProxy

from ffgraphql.types.app_primitives import ModelUserSearch
from ffgraphql.types.app_primitives import ModelSearch
from ffgraphql.types.app_primitives import ModelSearchDescriptor
from ffgraphql.types.app_primitives import TypeSearch
from ffgraphql.types.ct_primitives import TypeEnumGender
from ffgraphql.types.ct_primitives import EnumGender
from ffgraphql.utils import check_auth
from ffgraphql.mutations.utils import clean_auth0_user_id
from ffgraphql.mutations.utils import get_user
from ffgraphql.mutations.utils import get_search
from ffgraphql.mutations.utils import delete_search
from ffgraphql.mutations.utils import delete_search_descriptors


class InputSearch(graphene.InputObjectType):
    """ Input-type class used to provide input via GraphQL when creating or
        updating a `Search` record.
    """

    search_uuid = graphene.UUID(required=True)
    title = graphene.String(required=True)
    gender = graphene.Field(type=TypeEnumGender, required=False)
    year_beg = graphene.Int(required=False)
    year_end = graphene.Int(required=False)
    age_beg = graphene.Int(required=False)
    age_end = graphene.Int(required=False)


class MutationSearchUpsert(graphene.Mutation):
    """ GraphQL mutation class permitting the upsert operation of `ModelSearch`
        records.
    """

    class Arguments:
        auth0_user_id = graphene.String(
            description=("The Auth0 ID of the user against which this search "
                         "is upserted."),
            required=True,
        )
        search = InputSearch(
            description="The search to upsert.",
            required=True,
        )
        mesh_descriptor_ids = graphene.List(of_type=graphene.Int)

    search = graphene.Field(TypeSearch)

    @staticmethod
    def mutate(
        args: Dict,
        info: graphql.execution.base.ResolveInfo,
        auth0_user_id: str,
        search: InputSearch,
        mesh_descriptor_ids: List[int],
    ):
        """ Upserts a `ModelSearch` record based on the `search` input.

        Returns
            MutationSearchUpsert: The result of the mutation.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(auth0_user_id=str(auth0_user_id))

        # Check that the requesting user is authorized to make changes to the
        # user with the given Auth0 ID.
        check_auth(info=info, auth0_user_id=auth0_user_id)

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Retrieve the `ModelUser` record object.
        user = get_user(session=session, auth0_user_id=auth0_user_id)

        # Raise an exception if the requested user could not be found.
        if not user:
            msg = "User with Auth0 ID '{}' could not be found."
            msg_fmt = msg.format(auth0_user_id)
            raise graphql.GraphQLError(message=msg_fmt)

        # Upsert the `ModelSearch` record.
        statement = insert(
            ModelSearch,
            values={
                "search_uuid": search.search_uuid,
                "title": search.title,
                "gender": EnumGender.get_member(value=str(search.gender))
                if search.gender else None,
                "year_beg": search.year_beg,
                "year_end": search.year_end,
                "age_beg": search.age_beg,
                "age_end": search.age_end,
            }
        ).on_conflict_do_nothing()  # type: Insert
        # Execute the upsert.
        session.execute(statement)  # type: ResultProxy

        # Retrieve the newly upserted `ModelSearch` record object.
        search = get_search(session=session, search_uuid=search.search_uuid)

        # Upsert a `ModelUserSearch` record.
        statement = insert(
            ModelUserSearch,
            values={
                "user_id": user.user_id,
                "search_id": search.search_id,
            }
        ).on_conflict_do_nothing()  # type: Insert
        # Execute the upsert.
        session.execute(statement)  # type: ResultProxy

        # Delete all existing `ModelSearchDescriptor` records for the given
        # search so they can be replaced with new ones.
        delete_search_descriptors(session=session, search_id=search.search_id)

        # Upsert a `ModelSearchDescriptor` record for each of the defined
        # descriptors.
        for mesh_descriptor_id in mesh_descriptor_ids:
            statement = insert(
                ModelSearchDescriptor,
                values={
                    "search_id": search.search_id,
                    "descriptor_id": mesh_descriptor_id,
                }
            ).on_conflict_do_nothing()  # type: Insert
            # Execute the upsert.
            session.execute(statement)  # type: ResultProxy

        session.commit()

        return MutationSearchUpsert(search=search)


class MutationSearchDelete(graphene.Mutation):
    """ GraphQL mutation class permitting the deletion of `ModelSearch`
        records.
    """

    class Arguments:
        auth0_user_id = graphene.String(
            description=("The Auth0 ID of the user against which this search "
                         "is upserted."),
            required=True,
        )
        search_uuid = graphene.UUID(
            description="The search to upsert.",
            required=True,
        )

    search = graphene.Field(TypeSearch)

    @staticmethod
    def mutate(
        args: Dict,
        info: graphql.execution.base.ResolveInfo,
        auth0_user_id: str,
        search_uuid: uuid.UUID,
    ):
        """ Deletes a `ModelSearch` record and all its `ModelSearchDescriptor`
            records.

        Returns
            MutationSearchUpsert: The result of the mutation.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(auth0_user_id=str(auth0_user_id))

        # Check that the requesting user is authorized to make changes to the
        # user with the given Auth0 ID.
        check_auth(info=info, auth0_user_id=auth0_user_id)

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Retrieve the `ModelUser` record object.
        user = get_user(session=session, auth0_user_id=auth0_user_id)

        # Raise an exception if the requested user could not be found.
        if not user:
            msg = "User with Auth0 ID '{}' could not be found."
            msg_fmt = msg.format(auth0_user_id)
            raise graphql.GraphQLError(message=msg_fmt)

        # Retrieve the `ModelSearch` record object.
        search = get_search(session=session, search_uuid=search_uuid)

        # Raise an exception if the requested search could not be found.
        if not search:
            msg = ("Search with UUID '{}' under user with Auth0 ID '{}' "
                   "could not be found.")
            msg_fmt = msg.format(search_uuid, auth0_user_id)
            raise graphql.GraphQLError(message=msg_fmt)

        # Delete the `ModelSearch` record and all its related `ModelUserSearch`
        # and `ModelSearchDescriptor` records.
        delete_search(session=session, search_id=search.search_id)

        session.commit()

        return MutationSearchDelete(search=search)
