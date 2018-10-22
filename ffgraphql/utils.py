# coding=utf-8

import re
from typing import List, Dict, Union, Type, Optional

import sqlalchemy
import graphene
import sqlalchemy.orm
import graphql
from graphql.language.ast import FragmentSpread
from graphql.language.ast import Field
from graphene.utils.str_converters import to_snake_case

from fform.orm_base import OrmBase


def to_snake_case_plus(name: str) -> str:
    """Extends the `to_snake_case` function to account for numbers in the name
    separated by underscores.

    Args:
        name (str): The camel-case name to be converted to snake-case.

    Returns
        str: The converted name.
    """
    
    name_new = to_snake_case(name=name)
    for entry in list(set(re.findall("\d+", name_new))):
        name_new = name_new.replace(entry, "_{}".format(entry))
    return name_new


def extract_requested_fields(
    info: graphql.execution.base.ResolveInfo,
    fields: List[Union[Field, FragmentSpread]],
    do_convert_to_snake_case: bool = True,
) -> Dict:
    """Extracts the fields requested in a GraphQL query by processing the AST
    and returns a nested dictionary representing the requested fields.

    Note:
        This function should support arbitrarily nested field structures
        including fragments.

    Example:
        Consider the following query passed to a resolver and running this
        function with the `ResolveInfo` object passed to the resolver.

        >>> query = "query getAuthor{author(authorId: 1){nameFirst, nameLast}}"
        >>> extract_requested_fields(info, info.field_asts, True)
        {'author': {'name_first': None, 'name_last': None}}

    Args:
        info (graphql.execution.base.ResolveInfo): The GraphQL query info passed
            to the resolver function.
        fields (List[Union[Field, FragmentSpread]]): The list of `Field` or
            `FragmentSpread` objects parsed out of the GraphQL query and stored
            in the AST.
        do_convert_to_snake_case (bool): Whether to convert the fields as they
            appear in the GraphQL query (typically in camel-case) back to
            snake-case (which is how they typically appear in ORM classes).

    Returns:
        Dict: The nested dictionary containing all the requested fields.
    """

    result = {}
    for field in fields:

        # Set the `key` as the field name.
        key = field.name.value

        # Convert the key from camel-case to snake-case (if required).
        if do_convert_to_snake_case:
            key = to_snake_case_plus(name=key)

        # Initialize `val` to `None`. Fields without nested-fields under them
        # will have a dictionary value of `None`.
        val = None

        # If the field is of type `Field` then extract the nested fields under
        # the `selection_set` (if defined). These nested fields will be
        # extracted recursively and placed in a dictionary under the field
        # name in the `result` dictionary.
        if isinstance(field, Field):
            if (
                hasattr(field, "selection_set") and
                field.selection_set is not None
            ):
                # Extract field names out of the field selections.
                val = extract_requested_fields(
                    info=info,
                    fields=field.selection_set.selections,
                )
            result[key] = val
        # If the field is of type `FragmentSpread` then retrieve the fragment
        # from `info.fragments` and recursively extract the nested fields but
        # as we don't want the name of the fragment appearing in the result
        # dictionary (since it does not match anything in the ORM classes) the
        # result will simply be result of the extraction.
        elif isinstance(field, FragmentSpread):
            # Retrieve referened fragment.
            fragment = info.fragments[field.name.value]
            # Extract field names out of the fragment selections.
            val = extract_requested_fields(
                info=info,
                fields=fragment.selection_set.selections,
            )
            result = val

    return result


def _get_load_only_fields(
    fields_all: Dict,
    inspection: sqlalchemy.orm.Mapper,
) -> List[str]:
    """Retrieves the load-only fields out of the requested fields of a GraphQL
    query.

    This function retrieves the load-only fields for a given queried ORM class
    out the requested fields of a GraphQL query using that ORM class'
    inspection. The result of this function can be used in a `load_only` option
    function.

    Note:
        This function assumes that the top level of the `fields_all`
        dictionary refers directly to the class for which the `inspection`
        was performed.

    Args:
        fields_all (Dict): The GraphQL fields requested top-leveled to the
            queried ORM class.
        inspection (sqlalchemy.orm.Mapper): An inspection of the queried
            ORM class performed with the `sqlalchemy.inspect` function.

    Returns:
        List[str]: The list of keys to be used in the `load_only` function.
    """

    # Retrieve the fields pertaining to the queried ORM class by filtering
    # down to the top-fields that are columns in the ORM class.
    keys = [key for key in fields_all.keys() if key in inspection.columns]

    return keys


def _get_query_options(
    fields_all: Dict,
    inspection: sqlalchemy.orm.Mapper,
    option: Optional[sqlalchemy.orm.strategy_options.Load] = None
) -> List[sqlalchemy.orm.strategy_options.Load]:
    """Collects `load_only` and `joinedload` SQLAlchemy Query options based on
    a GraphQL query accounting for arbitrarily-nested relationships.

    This function operates in a recursive fashion and collects `load_only` and
    `joinedload` options for an SQLAlchemy Query object thus limiting the
    loaded fields of the queried ORM class/table to those requested in the
    GraphQL query. In addition, this function supports arbitrarily nested
    relationships to the root ORM class adding `joinedload` options to preclude
    lazy-loading of those relationships in addition to applying `load_only`
    options to the relationships themselves.

    Args:
        fields_all (Dict): The GraphQL fields requested top-leveled to the
            queried ORM class.
        inspection (sqlalchemy.orm.Mapper): An inspection of the queried
            ORM class performed with the `sqlalchemy.inspect` function.
        option (Optional[sqlalchemy.orm.strategy_options.Load]): The root option
            upon which more options will be chained as required. Defaults to
            `None`

    Returns:
        List[sqlalchemy.orm.strategy_options.Load]: A list of the collected
            options to be applied to the SQLAlchemy query via the `options`
            method.
    """

    # If not `option` is given then create a 'root' option by adding a
    # `load_only` for the fields defined for the ORM class.
    if option is None:
        fields_lo = _get_load_only_fields(
            inspection=inspection,
            fields_all=fields_all
        )
        option = sqlalchemy.orm.load_only(*fields_lo)

    # Retrieve the names of all relationship attributes of the ORM class out of
    # the requested fields using the provided `inspection`.
    names_rels = [
        key for key in fields_all.keys()
        if key in inspection.relationships
    ]

    # Create an empty list that will hold all the created options. This list is
    # needed as each relationship needs to be defined in distinct options.
    options = []

    # If the ORM class does not have any relationships defined in the requested
    # fields then simply add the provided `option` to `options`. The next loop
    # will then be skipped and only that `option` will be returned.
    if not names_rels:
        options.append(option)

    # Iterate over the requested relationships
    for name_rel in names_rels:
        # Retrieve the fields requested under this relationship.
        fields_rel = fields_all[name_rel]
        # Retrieve the relationship property out of the inspection.
        prop_rel = inspection.relationships[name_rel]
        # Retrieve the ORM class this relationship pertains to.
        class_rel = prop_rel.mapper.class_
        # Retrieve the relationship attribute under the original ORM class.
        attr_rel = getattr(inspection.class_, name_rel)
        # Perform an inspection on the relationship's ORM class.
        inspection_rel = sqlalchemy.inspect(class_rel)
        # Retrieve the load-only fields for the relationships's ORM class.
        fields_lo_rel = _get_load_only_fields(
            inspection=inspection_rel,
            fields_all=fields_rel,
        )
        # Chain a `joinedload` option to the original `option` join-loading the
        # requested relationship. In addition, chain a `load_only` limiting to
        # requested fields for that relationship only.
        _option = option.joinedload(attr_rel).load_only(*fields_lo_rel)
        # Recurse into the relationship in order to chain any relationships that
        # may be nested under it.
        options += _get_query_options(
            fields_all=fields_rel,
            inspection=inspection_rel,
            option=_option,
        )

    return options


def apply_requested_fields(
    info: graphql.execution.base.ResolveInfo,
    query: sqlalchemy.orm.Query,
    orm_class: Type[OrmBase],
    fields: Optional[Dict] = None,
) -> sqlalchemy.orm.Query:
    """Updates the SQLAlchemy Query object by adding `load_only` and
    `joinedload` option.

    This function updates an SQLAlchemy Query object limiting the loaded fields
    of the queried ORM class/table to those requested in the GraphQL query. In
    addition, this function supports arbitrarily nested relationships to the
    root ORM class adding `joinedload` options to preclude lazy-loading of
    those relationships in addition to applying `load_only` options to the
    relationships themselves.

    Note:
        This function assumes that the SQLAlchemy query only selects a single
        ORM class/table at the root of the query.

    Args:
        info (graphql.execution.base.ResolveInfo): The GraphQL query info passed
            to the resolver function.
        query (sqlalchemy.orm.Query): The SQLAlchemy Query object to be updated.
        orm_class (Type[OrmBaseMixin]): The ORM class of the selected table.
        fields (Optional[Dict]): Pre-extracted requested fields. If
            provided extraction is skipped.

    Returns:
        sqlalchemy.orm.Query: The updated SQLAlchemy Query object.
    """

    # Extract the fields requested in the GraphQL query unless they were
    # provided.
    if not fields:
        fields = extract_requested_fields(
            info=info,
            fields=info.field_asts,
            do_convert_to_snake_case=True,
        )

    # We assume that the top level of the `fields` dictionary only contains a
    # single key referring to the GraphQL resource being resolved.
    tl_key = list(fields.keys())[0]

    # Retrieve the `load_only` and `joinedload` options to be applied to the
    # query in a recursive fashion accounting for arbitrarily nested
    # relationships.
    options = _get_query_options(
        fields_all=fields[tl_key],
        inspection=sqlalchemy.inspect(orm_class)
    )

    # Apply the retrieved options to the query.
    query = query.options(*options)

    return query


def check_auth(
    info: graphene.ResolveInfo,
    auth0_user_id: str,
):
    """ Checks whether the access-token provided in the request authorizes the
        caller to access resources pertaining to a specific user.

    Note:
        As in service-to-service requests there is not user ID in the
        access-token, any requests where the access-token contains a  `sub`
        including the API's `auth0_client_id` are considered authorized.

    Args:
        info (graphene.ResolveInfo): The resolver info.
        auth0_user_id (str): The Auth0 user ID against which the check is
            performed.

    Raises:
        falcon.HTTPError: Raised with a 403 response if the incoming
            request is unathorized.
    """

    # Retrieve the application configuration and JWT token payload out of
    # the context.
    token_payload = info.context.get("token_payload")
    cfg = info.context.get("cfg")

    # If the value of the token `sub` field does not contain either the
    # provided `customer_id` or the configured `client_id` (used in
    # service-to-service requests) then the response is authorized hence
    # a 403 exception is raised.
    if (
        auth0_user_id not in token_payload["sub"] and
        cfg.auth0.client_id not in token_payload["sub"]
    ):
        msg = ("'Authorization' token does not grant access to user with "
               "ID '{}'.")
        msg_fmt = msg.format(auth0_user_id)

        raise graphql.GraphQLError(message=msg_fmt)
