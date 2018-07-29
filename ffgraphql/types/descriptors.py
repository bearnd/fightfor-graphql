# coding=utf-8

from typing import List, Dict, Union

import sqlalchemy.orm
from sqlalchemy import func as sqlalchemy_func
import graphene

from ffgraphql.types.mt_primitives import ModelDescriptor
from ffgraphql.types.mt_primitives import ModelTreeNumber
from ffgraphql.types.mt_primitives import ModelDescriptorSynonym
from ffgraphql.types.mt_primitives import TypeDescriptor


class TypeDescriptors(graphene.ObjectType):

    by_ui = graphene.Field(
        type=TypeDescriptor,
        description="Retrieve a MeSH descriptor through its UI.",
        ui=graphene.Argument(type=graphene.String, required=True),
    )

    by_tree_number_prefix = graphene.List(
        of_type=TypeDescriptor,
        description=("Retrieve a list of MeSH descriptors matching a "
                     "tree-number prefix."),
        tree_number_prefix=graphene.Argument(
            type=graphene.String,
            required=True,
        ),
    )

    by_synonym = graphene.List(
        of_type=TypeDescriptor,
        description=("Retrieve a list of MeSH descriptors fuzzy-matching a "
                     "synonym."),
        synonym=graphene.Argument(
            type=graphene.String,
            required=True,
        ),
        limit=graphene.Argument(
            type=graphene.Int,
            required=False,
        )
    )

    @staticmethod
    def resolve_by_ui(
        args: dict,
        info: graphene.ResolveInfo,
        ui: str
    ) -> ModelDescriptor:
        """Retrieves a `ModelDescriptor` object through its UI.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            ui (str): The UI of the `ModelDescriptor` to retrieve.

        Returns:
             DescriptorModel: The retrieved `ModelDescriptor` object or `None`
                if no match was not found.
        """

        # Retrieve the query on `ModelDescriptor`.
        query = TypeDescriptor.get_query(
            info=info,
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `ModelDescriptor` record matching `ui`.
        query = query.filter(ModelDescriptor.ui == ui)

        obj = query.first()

        return obj

    @staticmethod
    def resolve_by_tree_number_prefix(
        args: dict,
        info: graphene.ResolveInfo,
        tree_number_prefix: str
    ) -> List[ModelDescriptor]:
        """Retrieves a list of `ModelDescriptor` objects with a tree-number
        prefix-matching `tree_number_prefix`.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            tree_number_prefix (str): The tree-number prefix to match against.

        Returns:
             list[DescriptorModel]: The list of matched `ModelDescriptor`
                objects or an empty list if no match was found.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Query out `ModelDescriptor`.
        query = session.query(ModelDescriptor)  # type: sqlalchemy.orm.Query
        query = query.join(ModelDescriptor.tree_numbers)
        # Filter down to `ModelDescriptor` objects with a tree-number
        # prefix-matching `tree_number_prefix`.
        query = query.filter(
            ModelTreeNumber.tree_number.like("{}%".format(tree_number_prefix)),
        )

        objs = query.all()
        print(objs)

        return objs

    @staticmethod
    def resolve_by_synonym(
        args: Dict,
        info: graphene.ResolveInfo,
        synonym: str,
        limit: Union[int, None] = None,
    ) -> List[ModelDescriptor]:
        """Retrieves a list of `ModelDescriptor` objects with a tree-number
        prefix-matching `tree_number_prefix`.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            synonym (str): The synonym query by which to perform the search.
            limit (int, optional): The number of closest-matching descriptors
                to return. Defaults to `None`.

        Returns:
             list[DescriptorModel]: The list of matched `ModelDescriptor`
                objects or an empty list if no match was found.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define a function to calculate the maximum similarity between a
        # descriptor's synonyms and the synonym query.
        func_similarity = sqlalchemy_func.max(sqlalchemy_func.similarity(
            ModelDescriptorSynonym.synonym,
            synonym,
        )).label("synonym_similarity")

        # Query out `ModelDescriptor`.
        query = session.query(ModelDescriptor)  # type: sqlalchemy.orm.Query
        query = query.join(ModelDescriptor.synonyms)
        query = query.filter(ModelDescriptorSynonym.synonym.op("%%")(synonym))
        query = query.order_by(func_similarity.desc())
        query = query.group_by(ModelDescriptor.descriptor_id)

        if limit is not None:
            query = query.limit(limit=limit)

        objs = query.all()

        return objs
