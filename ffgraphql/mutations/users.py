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
from ffgraphql.types.app_primitives import ModelUserStudy
from ffgraphql.types.app_primitives import ModelUserCitation
from ffgraphql.utils import check_auth
from ffgraphql.mutations.utils import clean_auth0_user_id
from ffgraphql.mutations.utils import get_user
from ffgraphql.mutations.utils import get_study
from ffgraphql.mutations.utils import get_citation
from ffgraphql.mutations.utils import delete_user_searches


class InputUser(graphene.InputObjectType):
    """ Input-type class used to provide input via GraphQL when creating or
        updating a `ModelUser` record.
    """

    auth0_user_id = graphene.String(required=True)
    email = graphene.String(required=True)


class InputUserStudy(graphene.InputObjectType):
    """ Input-type class used to provide input via GraphQL when creating or
        deleting a `ModelUserStudy` record.
    """

    auth0_user_id = graphene.String(required=True)
    nct_id = graphene.String(required=True)


class InputUserCitation(graphene.InputObjectType):
    """ Input-type class used to provide input via GraphQL when creating or
        deleting a `ModelUserCitation` record.
    """

    auth0_user_id = graphene.String(required=True)
    pmid = graphene.Int(required=True)


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


class MutationUserStudyUpsert(graphene.Mutation):
    """ GraphQL mutation class permitting the upsert operation of
        `ModelUserStudy` records.
    """

    class Arguments:
        user_study = InputUserStudy(required=True)

    user = graphene.Field(TypeUser)

    @staticmethod
    def mutate(
        args: Dict,
        info: graphql.execution.base.ResolveInfo,
        user_study: InputUserStudy,
    ):
        """ Upserts a `ModelUserStudy` record based on the `user_study` input.

        Returns
            MutationUserStudyUpsert: The result of the mutation.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(
            auth0_user_id=str(user_study.auth0_user_id),
        )

        # Retrieve the NCT ID of the defined study.
        nct_id = str(user_study.nct_id)

        # Check that the requesting user is authorized to upsert the user with
        # the given Auth0 ID.
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

        # Retrieve the `ModelStudy` record object.
        study = get_study(session=session, nct_id=nct_id)

        # Raise an exception if the requested study could not be found.
        if not study:
            msg = "Study with NCT ID '{}' could not be found."
            msg_fmt = msg.format(nct_id)
            raise graphql.GraphQLError(message=msg_fmt)

        # Upsert the `ModelUserStudy` record.
        statement = insert(
            ModelUserStudy,
            values={
                "user_id": user.user_id,
                "study_id": study.study_id,
            }
        ).on_conflict_do_nothing()  # type: Insert

        # Execute the upsert.
        result = session.execute(statement)  # type: ResultProxy

        # Retrieve the newly upserted `ModelUser` record object.
        obj = get_user(session=session, auth0_user_id=auth0_user_id)

        session.commit()

        return MutationUserStudyUpsert(user=obj)


class MutationUserCitationUpsert(graphene.Mutation):
    """ GraphQL mutation class permitting the upsert operation of
        `ModelUserCitation` records.
    """

    class Arguments:
        user_citation = InputUserCitation(required=True)

    user = graphene.Field(TypeUser)

    @staticmethod
    def mutate(
        args: Dict,
        info: graphql.execution.base.ResolveInfo,
        user_citation: InputUserCitation,
    ):
        """ Upserts a `ModelUserCitation` record based on the `user_citation`
            input.

        Returns
            MutationUserCitationUpsert: The result of the mutation.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(
            auth0_user_id=str(user_citation.auth0_user_id),
        )

        # Retrieve the PubMed ID of the defined citation.
        pmid = int(str(user_citation.pmid))

        # Check that the requesting user is authorized to upsert the user with
        # the given Auth0 ID.
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

        # Retrieve the `ModelCitation` record object.
        citation = get_citation(session=session, pmid=pmid)

        # Raise an exception if the requested citation could not be found.
        if not citation:
            msg = "Citation with PubMed ID '{}' could not be found."
            msg_fmt = msg.format(pmid)
            raise graphql.GraphQLError(message=msg_fmt)

        # Upsert the `ModelUserStudy` record.
        statement = insert(
            ModelUserCitation,
            values={
                "user_id": user.user_id,
                "citation_id": citation.citation_id,
            }
        ).on_conflict_do_nothing()  # type: Insert

        # Execute the upsert.
        result = session.execute(statement)  # type: ResultProxy

        # Retrieve the newly upserted `ModelCitation` record object.
        obj = get_user(session=session, auth0_user_id=auth0_user_id)

        session.commit()

        return MutationUserCitationUpsert(user=obj)


class MutationUserStudyDelete(graphene.Mutation):
    """ GraphQL mutation class permitting the delete operation of
        `ModelUserStudy` records.
    """

    class Arguments:
        user_study = InputUserStudy(required=True)

    user = graphene.Field(TypeUser)

    @staticmethod
    def mutate(
        args: Dict,
        info: graphql.execution.base.ResolveInfo,
        user_study: InputUserStudy,
    ):
        """ Deletes a `ModelUserStudy` record based on the `user_study` input.

        Returns
            MutationUserStudyDelete: The result of the mutation.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(
            auth0_user_id=str(user_study.auth0_user_id),
        )

        # Retrieve the NCT ID of the defined study.
        nct_id = str(user_study.nct_id)

        # Check that the requesting user is authorized to upsert the user with
        # the given Auth0 ID.
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

        # Retrieve the `ModelStudy` record object.
        study = get_study(session=session, nct_id=nct_id)

        # Raise an exception if the requested study could not be found.
        if not study:
            msg = "Study with NCT ID '{}' could not be found."
            msg_fmt = msg.format(nct_id)
            raise graphql.GraphQLError(message=msg_fmt)

        # Retrieve the `ModelUserStudy` record object.
        query = session.query(ModelUserStudy)
        query = query.filter(ModelUserStudy.user_id == user.user_id)
        query = query.filter(ModelUserStudy.study_id == study.study_id)
        user_study = query.one_or_none()

        # Raise an exception if the requested user-study could not be found.
        if not user_study:
            msg = ("User-study for user with Auth0 ID '{} and NCT ID '{}' "
                   "could not be found.")
            msg_fmt = msg.format(auth0_user_id, nct_id)
            raise graphql.GraphQLError(message=msg_fmt)

        # Delete the `ModelUserStudy` record.
        session.delete(user_study)

        # Retrieve the newly upserted `ModelUser` record object.
        obj = get_user(session=session, auth0_user_id=auth0_user_id)

        session.commit()

        return MutationUserStudyDelete(user=obj)


class MutationUserCitationDelete(graphene.Mutation):
    """ GraphQL mutation class permitting the delete operation of
        `ModelUserCitation` records.
    """

    class Arguments:
        user_citation = InputUserCitation(required=True)

    user = graphene.Field(TypeUser)

    @staticmethod
    def mutate(
        args: Dict,
        info: graphql.execution.base.ResolveInfo,
        user_citation: InputUserCitation,
    ):
        """ Deletes a `ModelUserCitation` record based on the `user_citation`
            input.

        Returns
            MutationUserCitationDelete: The result of the mutation.
        """

        # Cleanup the Auth0 user ID.
        auth0_user_id = clean_auth0_user_id(
            auth0_user_id=str(user_citation.auth0_user_id),
        )

        # Retrieve the PubMed ID of the defined study.
        pmid = int(str(user_citation.pmid))

        # Check that the requesting user is authorized to upsert the user with
        # the given Auth0 ID.
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

        # Retrieve the `ModelCitation` record object.
        citation = get_citation(session=session, pmid=pmid)

        # Raise an exception if the requested citation could not be found.
        if not citation:
            msg = "Citation with PubMed ID '{}' could not be found."
            msg_fmt = msg.format(pmid)
            raise graphql.GraphQLError(message=msg_fmt)

        # Retrieve the `ModelUserCitation` record object.
        query = session.query(ModelUserCitation)
        query = query.filter(ModelUserCitation.user_id == user.user_id)
        query = query.filter(
            ModelUserCitation.citation_id == citation.citation_id,
        )
        user_citation = query.one_or_none()

        # Raise an exception if the requested user-citation could not be found.
        if not user_citation:
            msg = ("User-citation for user with Auth0 ID '{} and PubMed "
                   "ID '{}' could not be found.")
            msg_fmt = msg.format(auth0_user_id, pmid)
            raise graphql.GraphQLError(message=msg_fmt)

        # Delete the `ModelUserCitation` record.
        session.delete(user_citation)

        # Retrieve the newly upserted `ModelUser` record object.
        obj = get_user(session=session, auth0_user_id=auth0_user_id)

        session.commit()

        return MutationUserCitationDelete(user=obj)
