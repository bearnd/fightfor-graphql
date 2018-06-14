# coding=utf-8

from typing import List, Dict, Union

import sqlalchemy.orm
from sqlalchemy import func as sqlalchemy_func
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_mt import Descriptor as DescriptorModel
from fform.orm_mt import TreeNumber as TreeNumberModel
from fform.orm_mt import DescriptorSynonym as DescriptorSynonymModel


class DescriptorType(SQLAlchemyObjectType):
    class Meta:
        model = DescriptorModel


class TreeNumberType(SQLAlchemyObjectType):
    class Meta:
        model = TreeNumberModel


class DescriptorsType(graphene.ObjectType):

    by_ui = graphene.Field(
        type=DescriptorType,
        description="Retrieve a MeSH descriptor through its UI.",
        ui=graphene.Argument(type=graphene.String, required=True),
    )

    by_tree_number_prefix = graphene.List(
        of_type=DescriptorType,
        description=("Retrieve a list of MeSH descriptors matching a "
                     "tree-number prefix."),
        tree_number_prefix=graphene.Argument(
            type=graphene.String,
            required=True,
        ),
    )

    by_synonym = graphene.List(
        of_type=DescriptorType,
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
    ) -> DescriptorModel:
        """Retrieves a `DescriptorModel` object through its UI.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            ui (str): The UI of the `DescriptorModel` to retrieve.

        Returns:
             DescriptorModel: The retrieved `DescriptorModel` object or `None`
                if no match was not found.
        """

        # Retrieve the query on `DescriptorModel`.
        query = DescriptorType.get_query(
            info=info,
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `DescriptorModel` record matching `ui`.
        query = query.filter(DescriptorModel.ui == ui)

        obj = query.first()

        return obj

    @staticmethod
    def resolve_by_tree_number_prefix(
        args: dict,
        info: graphene.ResolveInfo,
        tree_number_prefix: str
    ) -> List[DescriptorModel]:
        """Retrieves a list of `DescriptorModel` objects with a tree-number
        prefix-matching `tree_number_prefix`.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            tree_number_prefix (str): The tree-number prefix to match against.

        Returns:
             list[DescriptorModel]: The list of matched `DescriptorModel`
                objects or an empty list if no match was found.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Query out `DescriptorModel`.
        query = session.query(DescriptorModel)  # type: sqlalchemy.orm.Query
        query = query.join(DescriptorModel.tree_numbers)
        # Filter down to `DescriptorModel` objects with a tree-number
        # prefix-matching `tree_number_prefix`.
        query = query.filter(
            TreeNumberModel.tree_number.like("{}%".format(tree_number_prefix)),
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
    ) -> List[DescriptorModel]:
        """Retrieves a list of `DescriptorModel` objects with a tree-number
        prefix-matching `tree_number_prefix`.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            synonym (str): The synonym query by which to perform the search.
            limit (int, optional): The number of closest-matching descriptors
                to return. Defaults to `None`.

        Returns:
             list[DescriptorModel]: The list of matched `DescriptorModel`
                objects or an empty list if no match was found.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define a function to calculate the maximum similarity between a
        # descriptor's synonyms and the synonym query.
        func_similarity = sqlalchemy_func.max(sqlalchemy_func.similarity(
            DescriptorSynonymModel.synonym,
            synonym,
        )).label("synonym_similarity")

        # Query out `DescriptorModel`.
        query = session.query(DescriptorModel)  # type: sqlalchemy.orm.Query
        query = query.join(DescriptorModel.synonyms)
        query = query.filter(DescriptorSynonymModel.synonym.op("%%")(synonym))
        query = query.order_by(func_similarity.desc())
        query = query.group_by(DescriptorModel.descriptor_id)

        if limit is not None:
            query = query.limit(limit=limit)

        objs = query.all()

        return objs
