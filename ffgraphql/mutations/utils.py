# coding=utf-8

import uuid
from typing import Optional, List

import sqlalchemy.orm

from ffgraphql.types.app_primitives import ModelUser
from ffgraphql.types.app_primitives import ModelUserSearch
from ffgraphql.types.app_primitives import ModelSearch
from ffgraphql.types.app_primitives import ModelSearchDescriptor


def clean_auth0_user_id(auth0_user_id: str) -> str:
    """ Cleans an Auth0 user ID by removing the `auth0|` prefix.

    Args:
        auth0_user_id (str): The Auth0 user ID.

    Returns:
        str: The cleaned up Auth0 user ID.
    """

    # If the `auth0_user_id` starts with `auth0|` then remove that prefix.
    if auth0_user_id.startswith("auth0|"):
        auth0_user_id = auth0_user_id.replace("auth0|", "")

    return auth0_user_id


def get_user(
    session: sqlalchemy.orm.Session,
    auth0_user_id: str,
) -> Optional[ModelUser]:
    """ Retrieves a `ModelUser` record object via its Auth0 user ID.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy session that will be
            used to perform the interaction with the SQL database.
        auth0_user_id (str): The Auth0 user ID for which retrieval will be
            performed.

    Returns:
        ModelUser: The retrieved `ModelUser` record object or `None` if no
            matches were found.
    """

    query = session.query(ModelUser)
    query = query.filter(ModelUser.auth0_user_id == auth0_user_id)
    obj = query.one_or_none()  # type: ModelUser

    return obj


def get_search(
    session: sqlalchemy.orm.Session,
    search_uuid: uuid.UUID,
) -> Optional[ModelSearch]:
    """ Retrieves a `ModelSearch` record object via its UUID.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy session that will be
            used to perform the interaction with the SQL database.
        search_uuid (uuid.UUID): The search UUID for which retrieval will be
            performed.

    Returns:
        ModelSearch: The retrieved `ModelSearch` record object or `None` if no
            matches were found.
    """

    query = session.query(ModelSearch)
    query = query.filter(ModelSearch.search_uuid == search_uuid)
    obj = query.one_or_none()  # type: ModelSearch

    return obj


def delete_search_descriptors(
    session: sqlalchemy.orm.Session,
    search_id: int,
):
    """ Deletes all `ModelSearchDescriptor` records for a given search.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy session that will be
            used to perform the interaction with the SQL database.
        search_id (int): The search ID for which deletion will be performed.
    """

    query = session.query(ModelSearchDescriptor)
    query = query.filter(ModelSearchDescriptor.search_id == search_id)
    query.delete()


def delete_search(
    session: sqlalchemy.orm.Session,
    search_id: int,
):
    """ Deletes a `ModelSearch` record and all related  `ModelSearchDescriptor`
        and `ModelUserSearch` records.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy session that will be
            used to perform the interaction with the SQL database.
        search_id (int): The search ID for which deletion will be performed.
    """

    # Delete all related `ModelSearchDescriptor` records.
    delete_search_descriptors(session=session, search_id=search_id)

    # Delete `ModelUserSearch` record.
    query = session.query(ModelUserSearch)
    query = query.filter(ModelUserSearch.search_id == search_id)
    query.delete()

    # Delete `ModelSearch` record.
    query = session.query(ModelSearch)
    query = query.filter(ModelSearch.search_id == search_id)
    query.delete()


def delete_user_searches(
    session: sqlalchemy.orm.Session,
    user_id: int,
):
    """ Deletes all `ModelUserSearch` records for a given user along with the
        related `ModelSearch` and `ModelSearchDescriptor` records.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy session that will be
            used to perform the interaction with the SQL database.
        user_id (int): The user ID for which deletion will be performed.
    """

    # Retrieve all `ModelUserSearch` records for that user.
    query = session.query(ModelUserSearch)
    query = query.filter(ModelUserSearch.user_id == user_id)
    user_searches = query.all()  # type: List[ModelUserSearch]

    # Iterate over the retrieved `ModelUserSearch` records and delete them
    # along with their related records.
    for user_search in user_searches:
        delete_search(session=session, search_id=user_search.search_id)
