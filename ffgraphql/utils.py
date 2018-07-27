# coding=utf-8

import operator
from typing import List, Dict, Union, Type, Optional

import sqlalchemy
import graphql
from graphql.language.ast import FragmentSpread
from graphql.language.ast import Field
import graphene
from graphene.utils.str_converters import to_snake_case, to_camel_case
from graphene_sqlalchemy.registry import get_global_registry
from graphene_sqlalchemy.types import construct_fields
import sqlalchemy.orm

from fform.orm_base import OrmBase


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
            key = to_snake_case(name=key)

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


def apply_requested_fields(
    info: graphql.execution.base.ResolveInfo,
    query: sqlalchemy.orm.Query,
    orm_class: Type[OrmBase],
    fields: Optional[Dict[str, None]] = None,
) -> sqlalchemy.orm.Query:
    """Updates the SQLAlchemy Query object by limiting the loaded fields of the
    table and its relationship to the ones explicitly requested in the GraphQL
    query.

    Note:
        This function is fairly simplistic in that it assumes that (1) the
        SQLAlchemy query only selects a single ORM class/table and that (2)
        relationship fields are only one level deep, i.e., that requestd fields
        are either table fields or fields of the table relationship, e.g., it
        does not support fields of relationship relationships.

    Args:
        info (graphql.execution.base.ResolveInfo): The GraphQL query info passed
            to the resolver function.
        query (sqlalchemy.orm.Query): The SQLAlchemy Query object to be updated.
        orm_class (Type[OrmBaseMixin]): The ORM class of the selected table.
        fields (Optional[Dict[str, None]]): Pre-extracted requested fields. If
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
    # We assume that any keys that have a value of `None` (as opposed to
    # dictionaries) are fields of the primary table. In addition, any keys that
    # start with `__` are typically added by the GraphQL client and omitted.
    table_fields = [
        key for key, val in fields[tl_key].items()
        if (val is None and not key.startswith("__"))
    ]

    # We assume that any keys that have a value being a dictionary are
    # relationship attributes on the primary table with the keys in the
    # dictionary being fields on that relationship. Thus we create a list of
    # `[relatioship_name, relationship_fields]` lists to be used in the
    # `joinedload` definitions.
    relationship_fieldsets = [
        [key, val.keys()]
        for key, val in fields[tl_key].items()
        if isinstance(val, dict)
    ]

    # Assemble a list of `joinedload` definitions on the defined relationship
    # attribute name and the requested fields on that relationship.
    options_joinedloads = []
    for relationship_fieldset in relationship_fieldsets:
        relationship = relationship_fieldset[0]
        rel_fields = relationship_fieldset[1]
        options_joinedloads.append(
            sqlalchemy.orm.joinedload(
                getattr(orm_class, relationship)
            ).load_only(*rel_fields)
        )

    # Update the SQLAlchemy query by limiting the loaded fields on the primary
    # table as well as by including the `joinedload` definitions.
    query = query.options(
        sqlalchemy.orm.load_only(*table_fields),
        *options_joinedloads
    )

    return query


def create_class(name, argnames, base=graphene.InputObjectType):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # here, the argnames variable is the one passed to the
            # ClassFactory call
            if key not in argnames:
                msg = "Argument {} not valid for {}"
                msg_fmt = msg.format(key, self.__class__.__name__)
                raise TypeError(msg_fmt)
            setattr(self, key, value)
        base.__init__(self, name[:-len("Class")])
    newclass = type(name, (base,), {"__init__": __init__})
    return newclass


class FilterOperatorType(graphene.Enum):

    EQ = operator.eq
    NE = operator.ne
    GT = operator.gt
    LT = operator.lt
    LE = operator.le
    GE = operator.ge


def create_filter_class(name, field_name, value_type):
    def __init__(self, **kwargs):
        graphene.AbstractType.__init__(self)
    newclass = type(name, (graphene.AbstractType,), {"__init__": __init__})
    newclass._field = field_name
    newclass.value = value_type
    return newclass


def create_orm_filter_classes(orm_class):

    fields = construct_fields(orm_class, get_global_registry(), [], [])

    filter_classes = []
    for field_name, field in fields.items():
        name = "{}Filter{}".format(
            orm_class.__name__,
            to_camel_case(field_name).capitalize()
        )
        filter_class = create_filter_class(
            name=name,
            field_name=field_name,
            value_type=field.get_type()
        )
        filter_classes.append(filter_class)

    return filter_classes




