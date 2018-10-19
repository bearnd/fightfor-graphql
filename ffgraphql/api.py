# coding=utf-8

import attrdict
import falcon
import graphene
import sqlalchemy.orm

from ffgraphql.loggers import create_logger
from ffgraphql.middlewares.auth0 import MiddlewareCors
from ffgraphql.middlewares.auth0 import MiddlewareAuth0
from ffgraphql.resources import ResourceGraphQlSqlAlchemy


def create_api(
    cfg: attrdict.AttrDict,
    schema: graphene.Schema,
    scoped_session: sqlalchemy.orm.scoped_session,
    logger_level: str,
):
    """Creates a Falcon API and adds resources for the GraphQL endpoint.

    Args:
        cfg (attrdict.Attrdict): The application configuration loaded with the
            methods under the `config.py` module.
        schema (graphene.Schema): An instance of the Graphene schema to expose
            via the GraphQL endpoint.
        scoped_session (sqlalchemy.orm.scoped_session): A SQLAlchemy
            scoped-session that will be used to perform the interaction with
            the SQL database.
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
    api = falcon.API(
        middleware=[
            # Instantiate and add the CORS middleware.
            MiddlewareCors(logger_level=logger_level),
            # Instantiate and add the Auth0 authentication middleware.
            MiddlewareAuth0(
                auth0_domain=cfg.auth0.domain,
                auth0_audience=cfg.auth0.audience,
                auth0_jwks_url=cfg.auth0.jwks_url,
                logger_level=logger_level,
            ),
        ],
    )

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

    msg_fmt = u"API initialization complete."
    logger.info(msg_fmt)

    return api
