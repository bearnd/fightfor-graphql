# coding=utf-8

"""
This module defines a `MiddlewareCors` class meant to act as a middleware that
handles CORS OPTIONS preflight requests.
"""

import falcon

from ffgraphql.loggers import create_logger


class MiddlewareCors(object):
    """ Falcon middleware class handling CORS OPTIONS preflight requests."""

    def __init__(self, **kwargs):
        """ Constructor."""

        # Create a class-level logger.
        self.logger = create_logger(
            logger_name=type(self).__name__,
            logger_level=kwargs.get("logger_level", "DEBUG")
        )

    @staticmethod
    def is_req_cors(req: falcon.Request) -> bool:
        """ Checks whether the given request is a CORS OPTIONS preflight
            request.

        Args:
            req (falcon.Request): The Falcon `Request` object.

        Returns:
            bool: Whether the given request is a CORS OPTIONS preflight request.
        """

        # If the request method is not OPTIONS then this isn't a CORS OPTIONS
        # preflight request.
        if req.method != "OPTIONS":
            return False

        # If the request does not specify a `Access-Control-Request-Method`
        # header then this isn't a CORS OPTIONS preflight request.
        if not req.get_header("Access-Control-Request-Method"):
            return False

        return True

    def process_response(
        self,
        req: falcon.Request,
        resp: falcon.Response,
        resource: object,
        req_succeeded: bool,
    ):
        """ Intercepts outgoing responses and handles incoming CORS OPTIONS
            preflight requests.

        Args:
            req (falcon.Request): The Falcon `Request` object.
            resp (falcon.Response): The Falcon `Response` object.
            resource (object): Resource object to which the request was routed.
                May be None if no route was found for the request.
            req_succeeded (bool): True if no exceptions were raised while the
                framework processed and routed the request; otherwise False.
        """

        # Set the `Access-Control-Allow-Origin` header.
        resp.set_header('Access-Control-Allow-Origin', '*')

        # Skip the request if it doesn't exhibit the characteristics of a CORS
        # OPTIONS preflight request.
        if not self.is_req_cors(req=req):
            return None

        msg_fmt = "Processing CORS preflight OPTIONS request."
        self.logger.info(msg_fmt)

        # Retrieve and remove the `Allow` header from the response.
        allow = resp.get_header('Allow')
        resp.delete_header('Allow')

        # Retrieve the `Access-Control-Request-Headers` header from the
        # request.
        allow_headers = req.get_header(
            'Access-Control-Request-Headers',
            default='*'
        )

        # Set the appropriate CORS headers in the response.
        resp.set_header(name="Access-Control-Allow-Methods", value=allow)
        resp.set_header(
            name="Access-Control-Allow-Headers",
            value=allow_headers,
        )
        resp.set_header(name="Access-Control-Max-Age", value='86400')
