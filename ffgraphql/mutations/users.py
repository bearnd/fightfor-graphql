# coding=utf-8

from typing import Dict

import graphql
import graphene
import sqlalchemy.orm
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.engine.result import ResultProxy

from ffgraphql.types.app_primitives import ModelUser
from ffgraphql.types.app_primitives import TypeUser
from ffgraphql.utils import check_auth
from ffgraphql.mutations.utils import clean_auth0_user_id
from ffgraphql.mutations.utils import get_user
from ffgraphql.mutations.utils import delete_user_searches


class InputUser(graphene.InputObjectType):
    """ Input-type class used to provide input via GraphQL when creating or
        updating a `ModelUser` record.
    """

    auth0_user_id = graphene.String(required=True)
    email = graphene.String(required=True)


class MutationUserUpsert(graphene.Mutation):
    """ GraphQL mutation class permitting the upsert operation of `ModelUser`
        records.
    """

    class Arguments:
        user = InputUser(required=True)

    user = graphene.Field(TypeUser)

    @staticmethod
    def mutate(
        args: Dict,
        info: graphql.execution.base.ResolveInfo,
        user: InputUser,
    ):
        """ Upserts a `ModelUser` record based on the `user` input.

        Returns
            MutationUserUpsert: The result of the mutation.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(
            auth0_user_id=str(user.auth0_user_id),
        )

        # Check that the requesting user is authorized to upsert the user with
        # the given Auth0 ID.
        check_auth(info=info, auth0_user_id=auth0_user_id)

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Upsert the `ModelUser` record.
        statement = insert(
            ModelUser,
            values={
                "auth0_user_id": user.auth0_user_id,
                "email": user.email,
            }
        ).on_conflict_do_nothing()  # type: Insert

        # Execute the upsert.
        result = session.execute(statement)  # type: ResultProxy

        # Retrieve the newly upserted `ModelUser` record object.
        obj = get_user(session=session, auth0_user_id=auth0_user_id)

        session.commit()

        return MutationUserUpsert(user=obj)


class MutationUserDelete(graphene.Mutation):
    """ GraphQL mutation class permitting the deletion of `ModelUser`
        records.
    """

    class Arguments:
        auth0_user_id = graphene.String(required=True)

    user = graphene.Field(TypeUser)

    @staticmethod
    def mutate(
        args: Dict,
        info: graphql.execution.base.ResolveInfo,
        auth0_user_id: str,
    ):
        """ Deletes a `ModelUser` record based on the `user` input.

        Returns
            MutationUserDelete: The result of the mutation.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(auth0_user_id=str(auth0_user_id))

        # Check that the requesting user is authorized to upsert the user with
        # the given Auth0 ID.
        check_auth(info=info, auth0_user_id=auth0_user_id)

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Retrieve the `ModelUser` record object.
        query = session.query(ModelUser)
        query = query.filter(ModelUser.auth0_user_id == auth0_user_id)
        obj = query.one_or_none()  # type: ModelUser

        # Raise an exception if the requested user could not be found.
        if not obj:
            msg = "User with Auth0 ID '{}' could not be found."
            msg_fmt = msg.format(auth0_user_id)
            raise graphql.GraphQLError(message=msg_fmt)

        # Delete the `ModelSearch` records related to this user as well as all
        # `ModelUserSearch` and `ModelSearchDescriptor` records related to
        # those searches.
        delete_user_searches(session=session, user_id=obj.user_id)

        # Delete the `ModelUser` record.
        session.delete(obj)
        session.commit()

        return MutationUserDelete(user=obj)
