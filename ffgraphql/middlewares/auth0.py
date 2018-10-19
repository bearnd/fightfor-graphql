# coding=utf-8

"""
This module defines a `MiddlewareAuth0` class meant to act as a middleware that
validates an Auth0 access-token present in the `Authorization` header of
incoming requests and which responds with a 401 if the header or token are
missing or invalid.
"""

import re
from typing import List, Optional

import falcon
from jose import jwt
import requests

from ffgraphql.loggers import create_logger
from ffgraphql.excs import Auth0JwksRetrievalError
from ffgraphql.middlewares.cors import MiddlewareCors


class MiddlewareAuth0(object):
    """ Falcon middleware class validating Auth0 access-tokens present in the
        `Authorization` header of incoming requests.
    """

    ALGORITHMS = ["RS256"]

    def __init__(
        self,
        auth0_domain: str,
        auth0_audience: str,
        auth0_jwks_url: str,
        exlcude: Optional[List[str]] = None,
        **kwargs
    ):
        """ Constructor.

        Args:
            auth0_domain (str): The Auth0 domain.
            auth0_audience (str): The Auth0 audience.
            auth0_jwks_url (str): The URL where the Auth0 JSON Web Key Set can
                be retrieved from.
            exlcude (Optional[List[str]] = None): A list of path strings or
                regexes. Any path matching any of these will be excluded and
                won't be subjected to a authorization check.
        """

        # Internalize arguments.
        self.auth0_domain = auth0_domain
        self.auth0_audience = auth0_audience
        self.auth0_jwks_url = auth0_jwks_url
        if exlcude:
            self.exclude = exlcude
        else:
            self.exclude = []

        # Create a class-level logger.
        self.logger = create_logger(
            logger_name=type(self).__name__,
            logger_level=kwargs.get("logger_level", "DEBUG")
        )

        # Retrieve the Auth0 JWKS.
        self.jwks = self._get_jwks()

    def _get_jwks(self):
        """ Retrieves and JSON-decodes the Auth0 JSON Web Key Set from the URL
            defined upon instantiation.

        Returns:
            dict: The retrieved and decoded Auth0 JWKS.
        """

        msg = "Retrieving the Auth0 JSON Web Key Set from URL '{}'"
        msg_fmt = msg.format(self.auth0_jwks_url)
        self.logger.debug(msg_fmt)

        # Retrieve the JWKS.
        response = requests.get(url=self.auth0_jwks_url)

        if response.ok:
            jwks = response.json()
        else:
            msg = "Could not retrieve the Auth0 JSON Web Key Set from URL '{}'"
            msg_fmt = msg.format(self.auth0_jwks_url)
            self.logger.error(msg_fmt)
            raise Auth0JwksRetrievalError(msg_fmt)

        return jwks

    def _is_path_excluded(self, path):
        """ Checks if a given `path` matches any of the defined exclusions.

        Args:
            path (str): The path to be evaluated.

        Returns:
            bool: Whether the `path` matches any of the defined exclusions.
        """

        # Iterate over the exclusion regexes and attempt to match each of them
        # to the `path`. Should any match be found the path should be excluded
        # and `True` is returned.
        for exclusion in self.exclude:
            match = re.match(exclusion, path)
            if match is not None:
                return True

        return False

    def _get_token(
        self,
        req: falcon.Request,
    ) -> str:
        """ Validates the `Authorization` header and returns the token or
            raises 401 errors if the header is missing/invalid.

        Args:
            req (falcon.Request): The Falcon `Request` object.

        Returns:
            str: The token.
        """

        # Retrieve the `Authorization` header from the request.
        auth = req.get_header("Authorization")

        # If the `Authorization` header is missing then raise a 401.
        if not auth:
            msg_fmt = "'Authorization' header not found."
            self.logger.error(msg_fmt)

            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title="Missing 'Authorization' header.",
                description=msg_fmt,
            )

        parts = auth.split()

        # Perform basic structural checks on the content of the `Authorization`
        # header and raise a 401 is any of them fail.
        if parts[0].lower() != "bearer":
            msg_fmt = "'Authorization' header does not start with `Bearer`."
            self.logger.error(msg_fmt)

            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title="Invalid 'Authorization' header.",
                description=msg_fmt,
            )
        elif len(parts) == 1:
            msg_fmt = "No token found in 'Authorization' header."
            self.logger.error(msg_fmt)

            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title="Invalid 'Authorization' header.",
                description=msg_fmt,
            )
        elif len(parts) > 2:
            msg_fmt = ("'Authorization' header must follow a 'Bearer "
                       "<token>' format.")
            self.logger.error(msg_fmt)

            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title="Invalid 'Authorization' header.",
                description=msg_fmt,
            )

        token = parts[1]

        return token

    def process_request(
        self,
        req: falcon.Request,
        resp: falcon.Response,
    ):
        """ Intercepts incoming requests and performs an authorization check.

        Note:
            Requests to paths matching any of the `excluded` strings or regexes
            are not subjected to a check and immediately routed.

        Args:
            req (falcon.Request): The Falcon `Request` object.
            resp (falcon.Response): The Falcon `Response` object.
        """

        # Skip the authentication check if the current request is a CORS
        # OPTIONS request. The actual handling of the request will be handled
        # via the `MiddlewareCors` class.
        if MiddlewareCors.is_req_cors(req=req):
            return None

        # Skip the authentication check if the current path has been excluded.
        if self._is_path_excluded(req.path):
            return None

        # Validate the authorization header and retrieve the token.
        token = self._get_token(req=req)

        # Retrieve the token header and raise a 401 if the token is malformed
        # and the header can't be retrieved.
        try:
            unverified_header = jwt.get_unverified_header(token)
        except Exception:
            msg_fmt = "'Authorization' token is malformed."
            self.logger.exception(msg_fmt)

            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title="Malformed 'Authorization' token.",
                description=msg_fmt,
            )

        # Assemble the RSA key.
        rsa_key = {}
        for key in self.jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }

        # Validate and decode the access token and raise a 401 should it fail.
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=self.ALGORITHMS,
                    audience=self.auth0_audience,
                    issuer="https://{}/".format(self.auth0_domain)
                )
            except jwt.ExpiredSignatureError:
                msg_fmt = "'Authorization' token has expired."
                self.logger.exception(msg_fmt)

                raise falcon.HTTPError(
                    status=falcon.HTTP_401,
                    title="Expired 'Authorization' token.",
                    description=msg_fmt,
                )
            except Exception:
                msg_fmt = "'Authorization' header is invalid."
                self.logger.exception(msg_fmt)

                raise falcon.HTTPError(
                    status=falcon.HTTP_401,
                    title="Invalid 'Authorization' header.",
                    description=msg_fmt,
                )
        else:
            msg_fmt = ("Could not find appropriately key in 'Authorization'"
                       " header.")
            self.logger.error(msg_fmt)

            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title="Invalid 'Authorization' header.",
                description=msg_fmt,
            )

        # Add the token and decoded payload to the request context so they can
        # be used in the resources.
        req.context["token"] = token
        req.context["token_payload"] = payload
