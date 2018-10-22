# coding=utf-8

import json
import functools
from collections import OrderedDict
from typing import Dict

import attrdict
import graphene
import falcon

from ffgraphql.loggers import create_logger


class ResourceGraphQl(object):
    """Main GraphQL server. Integrates with the predefined Graphene schema."""

    def __init__(
        self,
        cfg: attrdict.AttrDict,
        schema: graphene.Schema,
    ):

        # Internalize arguments.
        self.cfg = cfg
        self.schema = schema

        # Create logger.
        self.logger = create_logger(
            logger_name=type(self).__name__,
            logger_level="DEBUG"
        )

        self._respond_no_query = functools.partial(
            self._respond_error,
            status=falcon.HTTP_400,
            message="Must provide query string.",
        )

        self._respond_invalid_variables = functools.partial(
            self._respond_error,
            status=falcon.HTTP_400,
            message="Variables are invalid JSON.",
        )

        self._respond_invalid_body = functools.partial(
            self._respond_error,
            status=falcon.HTTP_400,
            message="POST body sent invalid JSON.",
        )

    def _execute_query(
        self,
        query,
        variable_values,
        token: str,
        token_payload: Dict,
        operation_name=None,
    ):
        result = self.schema.execute(
            query,
            variable_values=variable_values,
            operation_name=operation_name,
            context_value={
                "cfg": self.cfg,
                "token": token,
                "token_payload": token_payload,
            }
        )

        return result

    @staticmethod
    def _respond_error(
        resp: falcon.Response,
        status: str,
        message: str,
    ):

        resp.status = status
        resp.body = json.dumps(
            {"errors": [{"message": message}]},
            separators=(',', ':')
        )

    def on_post(self, req, resp):
        """Handles GraphQL POST requests."""

        # parse url parameters in the request first
        if req.params and 'query' in req.params and req.params['query']:
            query = str(req.params['query'])
        else:
            query = None

        if 'variables' in req.params and req.params['variables']:
            try:
                variables = json.loads(str(req.params['variables']),
                                       object_pairs_hook=OrderedDict)
            except json.decoder.JSONDecodeError:
                return self._respond_invalid_variables(resp=resp)
        else:
            variables = None

        if 'operationName' in req.params and req.params['operationName']:
            operation_name = str(req.params['operationName'])
        else:
            operation_name = None

        # Next, handle 'content-type: application/json' requests
        if req.content_type and 'application/json' in req.content_type:
            # error for requests with no content
            if req.content_length in (None, 0):
                return self._respond_invalid_body(resp=resp)

            # read and decode request body
            raw_json = req.stream.read()
            try:
                req.context['post_data'] = json.loads(
                    raw_json.decode('utf-8'),
                    object_pairs_hook=OrderedDict
                )
            except json.decoder.JSONDecodeError:
                return self._respond_invalid_body(resp=resp)

            # build the query string (Graph Query Language string)
            if (
                query is None and req.context['post_data'] and
                'query' in req.context['post_data']
            ):
                query = str(req.context['post_data']['query'])
            elif query is None:
                return self._respond_no_query(resp=resp)

            # build the variables string (JSON string of key/value pairs)
            if (
                variables is None and
                req.context['post_data'] and
                'variables' in req.context['post_data'] and
                req.context['post_data']['variables']
            ):
                try:
                    variables = req.context['post_data']['variables']
                    if not isinstance(variables, OrderedDict):
                        json_str = str(req.context['post_data']['variables'])
                        variables = json.loads(
                            json_str,
                            object_pairs_hook=OrderedDict
                        )
                except json.decoder.JSONDecodeError:
                    self.logger.exception(variables)
                    return self._respond_invalid_variables(resp=resp)

            elif variables is None:
                variables = ""

            # build the operationName string (matches a query or mutation name)
            if (
                operation_name is None and
                'operationName' in req.context['post_data'] and
                req.context['post_data']['operationName']
            ):
                operation_name = str(req.context['post_data']['operationName'])

        # Alternately, handle 'content-type: application/graphql' requests
        elif req.content_type and 'application/graphql' in req.content_type:
            # read and decode request body
            req.context['post_data'] = req.stream.read().decode('utf-8')

            # build the query string
            if query is None and req.context['post_data']:
                query = str(req.context['post_data'])

            elif query is None:
                return self._respond_no_query(resp=resp)

        # Skip application/x-www-form-urlencoded since they are automatically
        # included by setting req_options.auto_parse_form_urlencoded = True

        elif query is None:
            # this means that the content-type is wrong and there aren't any
            # query params in the url
            return self._respond_no_query(resp=resp)

        # redirect stdout of schema.execute to /dev/null
        result = self._execute_query(
            query=query,
            variable_values=variables,
            token=req.context["token"],
            token_payload=req.context["token_payload"],
            operation_name=operation_name
        )

        # If the GraphQL execution resulted in errors then respond with a 200
        # but include the error messages out of the exceptions.
        if result.errors:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(
                {
                    "errors": [{
                        "message": str(error)
                    } for error in result.errors]
                },
                separators=(',', ':')
            )
            return None

        # If the GraphQL execution yielded results then construct the response
        # and return. Otherwise respond with a 500 error as the GraphQL
        # execution yielded neither results nor errors.
        if result.data:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(
                {
                    'data': result.data
                },
                separators=(',', ':')
            )
            return None
        else:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps(
                {
                    "errors": [{
                        "message": str(error)
                    } for error in result.errors]
                },
                separators=(',', ':')
            )
            return None


class ResourceGraphQlSqlAlchemy(ResourceGraphQl):
    """Main GraphQL server. Integrates with the predefined Graphene schema."""

    def __init__(
        self,
        cfg,
        schema,
        scoped_session,
    ):
        # Internalize arguments.
        self.scoped_session = scoped_session

        super(ResourceGraphQlSqlAlchemy, self).__init__(
            cfg=cfg,
            schema=schema
        )

    def _execute_query(
        self,
        query,
        variable_values,
        token: str,
        token_payload: Dict,
        operation_name=None,
    ):
        msg = "Executing query: {} with variables {}"
        msg_fmt = msg.format(query, variable_values)
        self.logger.debug(msg_fmt)

        result = self.schema.execute(
            query,
            variable_values=variable_values,
            operation_name=operation_name,
            context_value={
                "session": self.scoped_session,
                "cfg": self.cfg,
                "token": token,
                "token_payload": token_payload,
            }
        )

        return result
