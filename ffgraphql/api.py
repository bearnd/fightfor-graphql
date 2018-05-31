# coding=utf-8

import sqlalchemy.orm
import falcon
import graphene

from ffgraphql.loggers import create_logger
from ffgraphql.resources import ResourceGraphQlSqlAlchemy
from ffgraphql.resources import ResourceGraphiQL


def create_api(
    schema: graphene.Schema,
    scoped_session: sqlalchemy.orm.scoped_session,
    do_enable_graphiql: bool,
    path_graphiql: str,
    logger_level: str,
):
    """Creates a Falcon API and adds resources for the GraphQL and GraphiQL
    endpoints.

    Args:
        schema (graphene.Schema): An instance of the Graphene schema to expose
            via the GraphQL endpoint.
        scoped_session (sqlalchemy.orm.scoped_session): A SQLAlchemy
            scoped-session that will be used to perform the interaction with
            the SQL database.
        do_enable_graphiql (bool): Whether to expose the GraphiQL endpoint or
            not.
        path_graphiql (str): The path to the GraphiQL distribution that will be
            exposed via the GraphiQL endpoint.
        logger_level (str): The logger level to be set in the Falcon resource
            classes.

    Returns:
        falcon.api.API: The instantiate Falcon API.
    """
    # Create logger.
    logger = create_logger(
        logger_name=__name__,
        logger_level=logger_level
    )

    # Create the API.
    api = falcon.API()

    msg_fmt = u"Initializing API resources."
    logger.info(msg_fmt)

    # Add the GraphQL route.
    api.add_route(
        uri_template="/graphql",
        resource=ResourceGraphQlSqlAlchemy(
            schema=schema,
            scoped_session=scoped_session,
        )
    )

    # Add the GraphiQL routes (if defined).
    if do_enable_graphiql:
        api.add_route(
            uri_template="/graphiql/",
            resource=ResourceGraphiQL(
                path_graphiql=path_graphiql,
            )
        )
        api.add_route(
            uri_template="/graphiql/{static_file}",
            resource=ResourceGraphiQL(
                path_graphiql=path_graphiql,
            )
        )

    msg_fmt = u"API initialization complete."
    logger.info(msg_fmt)

    return api
