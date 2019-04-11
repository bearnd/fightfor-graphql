# coding=utf-8

from typing import List, Optional

import sqlalchemy
import sqlalchemy.orm
import graphene
from sqlalchemy.dialects import postgresql
from sqlalchemy import func as sqlalchemy_func

from ffgraphql.types.pubmed_primitives import TypeCitation
from ffgraphql.types.pubmed_primitives import ModelCitation
from ffgraphql.types.pubmed_primitives import ModelArticle
from ffgraphql.types.mt_primitives import ModelTreeNumber
from ffgraphql.types.mt_primitives import ModelDescriptor
from ffgraphql.types.mt_primitives import ModelDescriptorTreeNumber
from ffgraphql.utils import apply_requested_fields


class TypeCitations(graphene.ObjectType):

    by_id = graphene.List(
        of_type=TypeCitation,
        description="Retrieve PubMed citations through their IDs.",
        citation_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True,
        ),
    )

    by_pmid = graphene.List(
        of_type=TypeCitation,
        description="Retrieve PubMed citations through their PMIDs.",
        pmids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True,
        ),
    )

    search = graphene.List(
        of_type=TypeCitation,
        description=("Retrieve a list of PubMed citations matching several "
                     "filters."),
        mesh_descriptor_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            description=("MeSH descriptor primary-key IDs as they appear in "
                         "the `mesh.descriptors` table."),
            required=True
        ),
        year_beg=graphene.Argument(
            type=graphene.Int,
            description=("The lower end of the year-range the citation "
                         "article may have been published in."),
            required=False,
        ),
        year_end=graphene.Argument(
            type=graphene.Int,
            description=("The upper end of the year-range the citation "
                         "article may have been published in."),
            required=False,
        ),
        do_include_children=graphene.Argument(
            type=graphene.Boolean,
            description=("Whether to analyze the MeSH descriptor tree and "
                         "include the descriptor children when performing the"
                         "search."),
            required=False,
            default_value=True,
        )
    )

    @staticmethod
    def resolve_by_id(
        args: dict,
        info: graphene.ResolveInfo,
        citation_ids: List[int],
    ) -> List[ModelCitation]:
        """Retrieves `ModelCitation` record objects through their IDs.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            citation_ids (List[str]): The IDs for which `ModelCitation` record
                objects will be retrieved.

        Returns:
             List[ModelCitation]: The retrieved `ModelCitation` record objects
                or an empty list if no matches were found.
        """

        # Retrieve the query on `ModelCitation`.
        query = TypeCitation.get_query(
            info=info,
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `ModelCitation` records matching any of the
        # `citation_ids`.
        query = query.filter(ModelCitation.citation_id.in_(citation_ids))

        # Limit query to fields requested in the GraphQL query adding
        # `load_only` and `joinedload` options as required.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelCitation,
        )

        objs = query.all()

        return objs

    @staticmethod
    def resolve_by_pmid(
        args: dict,
        info: graphene.ResolveInfo,
        pmids: List[int],
    ) -> List[ModelCitation]:
        """Retrieves `ModelCitation` record objects through their PMIDs.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            pmids (List[str]): The PMIDs for which `ModelCitation` record
                objects will be retrieved.

        Returns:
             List[ModelCitation]: The retrieved `ModelCitation` record objects
                or an empty list if no matches were found.
        """

        # Retrieve the query on `ModelCitation`.
        query = TypeCitation.get_query(
            info=info,
        )  # type: sqlalchemy.orm.query.Query

        # Filter to the `ModelCitation` records matching any of the
        # `citation_ids`.
        query = query.filter(ModelCitation.pmid.in_(pmids))

        # Limit query to fields requested in the GraphQL query adding
        # `load_only` and `joinedload` options as required.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelCitation,
        )

        objs = query.all()

        return objs

    @staticmethod
    def resolve_search(
        args: dict,
        info: graphene.ResolveInfo,
        mesh_descriptor_ids: List[int],
        year_beg: Optional[int] = None,
        year_end: Optional[int] = None,
        do_include_children: Optional[bool] = True,
    ) -> List[ModelCitation]:
        """Retrieves a list of `ModelCitation` objects matching several optional
        filters.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            mesh_descriptor_ids (List[int]): A list of MeSH descriptor IDs of
                the descriptors tagged against the study.
            year_beg (Optional[int]): The minimum year the publication date the
                article of a matched `ModelCitation` may have.
            year_end (Optional[int]): The maximum year the publication date the
                article of a matched `ModelCitation` may have.
            do_include_children (Optional[bool]): Whether to search for and
                include in the search the children MeSH descriptors of the
                provided descriptors.

        Returns:
             List[ModelCitation]: The list of matched `ModelCitation` objects
                or an empty list if no match was found.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # If the search is to account for the provided descriptors and their
        # children then find all the children descriptor IDs. Otherwise only
        # use the provided ones.
        if do_include_children:
            # Retrieve all tree-numbers for the specified MeSH descriptors.
            query_tns = session.query(
                ModelTreeNumber.tree_number,
                ModelDescriptorTreeNumber.descriptor_id,
            )
            query_tns = query_tns.join(ModelTreeNumber.descriptor_tree_numbers)
            query_tns = query_tns.filter(
                ModelDescriptorTreeNumber.descriptor_id.in_(
                    mesh_descriptor_ids,
                ),
            )
            # Retrieve the tree-numbers and associate them with each provided
            # descriptor ID in `map_descriptor_tns`.
            map_descriptor_tns = {}
            tree_numbers_all = []
            for tree_number, descriptor_id in query_tns.all():
                map_descriptor_tns.setdefault(
                    descriptor_id,
                    [],
                ).append(tree_number)
                tree_numbers_all.append(tree_number)

            # Deduplicate the tree-numbers.
            tree_numbers_all = list(set(tree_numbers_all))

            # If no tree-numbers have been found return an empty list.
            if not tree_numbers_all:
                return []

            # Query out the IDs of all children descriptors of all provided
            # descriptors based on the retrieved tree-numbers.
            query_descs = session.query(
                ModelDescriptor.descriptor_id,
                ModelTreeNumber.tree_number,
            )
            query_descs = query_descs.join(ModelDescriptor.tree_numbers)
            # Children descriptors are found by retrieving all descriptors
            # with any tree number prefixed by one of the previously found
            # tree-numbers.
            query_descs = query_descs.filter(
                ModelTreeNumber.tree_number.like(
                    sqlalchemy.any_(postgresql.array(
                        tuple([
                            "{}%".format(tn)
                            for tn in tree_numbers_all
                        ])
                    ))
                )
            )

            # Retrieve the children descriptor IDs and associate them with each
            # provided descriptor ID in `map_descriptor_children`.
            map_descriptor_children = {}
            for child_descriptor_id, tree_number in query_descs.all():
                for descriptor_id, tree_numbers in map_descriptor_tns.items():
                    for tree_number_prefix in tree_numbers:
                        if tree_number.startswith(tree_number_prefix):
                            map_descriptor_children.setdefault(
                                descriptor_id,
                                [descriptor_id],
                            ).append(child_descriptor_id)
            # Unique the descriptor IDs under each provided descriptor ID.
            for descriptor_id, tree_numbers in map_descriptor_children.items():
                map_descriptor_children[descriptor_id] = list(set(tree_numbers))
        else:
            map_descriptor_children = {
                descriptor_id: [descriptor_id]
                for descriptor_id in mesh_descriptor_ids
            }

        # If no descriptor IDs have been found return an empty list.
        if not map_descriptor_children:
            return []

        # Create a function to aggregate the MeSH descriptor IDs of queried
        # citations into an array.
        array_descriptors = sqlalchemy_func.array_agg(
            ModelDescriptor.descriptor_id,
        )

        # Find all PubMed citations associated with the MeSH descriptors found
        # prior.
        query = session.query(ModelCitation)

        # Filter citations by associated mesh-descriptors.
        query = query.join(ModelCitation.descriptors)

        if year_beg or year_end:
            query = query.join(ModelCitation.article)

        # Filter studies the year of their start-date.
        if year_beg:
            query = query.filter(
                ModelArticle.publication_year >= year_beg
            )
        if year_end:
            query = query.filter(
                ModelArticle.publication_year <= year_end
            )

        # Group by citation ID assembling the MeSH descriptor IDs of each study
        # into arrays. Each citation will pass the filters if it has at least
        # one of the descriptors under the provided descriptors (which will be
        # multiple if children descriptors are used). This is achieved through
        # the overlap `&&` operator which returns `true` if one array shares at
        # least one element with the other.
        query = query.group_by(ModelCitation.citation_id)
        query = query.having(
            sqlalchemy.and_(
                *[
                    array_descriptors.op("&&")(
                        sqlalchemy_func.cast(
                            descriptor_ids,
                            postgresql.ARRAY(postgresql.BIGINT),
                        )
                    )
                    for descriptor_ids in map_descriptor_children.values()
                ]
            )
        )

        # Limit query to fields requested in the GraphQL query.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelCitation,
        )

        objs = query.all()

        return objs
