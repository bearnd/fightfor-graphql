# coding=utf-8

from typing import List, Optional

import sqlalchemy
import sqlalchemy.orm
import graphene
from sqlalchemy.dialects import postgresql

from ffgraphql.types.pubmed_primitives import TypeCitation
from ffgraphql.types.pubmed_primitives import ModelCitation
from ffgraphql.types.pubmed_primitives import ModelArticle
from ffgraphql.types.mt_primitives import ModelTreeNumber
from ffgraphql.types.mt_primitives import ModelDescriptor
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
        # children the find all the children descriptor IDs. Otherwise only
        # use the provided ones.
        if do_include_children:
            # Retrieve all tree-numbers for the specified MeSH descriptors.
            query_tns = session.query(ModelTreeNumber.tree_number)
            query_tns = query_tns.join(ModelTreeNumber.descriptors)
            query_tns = query_tns.filter(
                ModelDescriptor.descriptor_id.in_(mesh_descriptor_ids),
            )
            # Retrieve the tree-numbers and get them out of their encompassing
            # tuple.
            tree_numbers = [tn[0] for tn in query_tns.all()]

            # If no tree-numbers have been found return an empty list.
            if not tree_numbers:
                return []

            # Find all UIs of the descriptors and their children for the found
            # tree-numbers.
            query_descs = session.query(ModelDescriptor.descriptor_id)
            query_descs = query_descs.join(ModelDescriptor.tree_numbers)
            query_descs = query_descs.filter(
                ModelTreeNumber.tree_number.like(
                    sqlalchemy.any_(postgresql.array(
                        tuple(["{}%".format(tn) for tn in tree_numbers])
                    ))
                )
            )

            # Retrieve the descriptor IDs, get them out of their encompassing
            # tuples, and unique them.
            descriptor_ids = list(set([d[0] for d in query_descs.all()]))
        else:
            descriptor_ids = mesh_descriptor_ids

        # If no descriptor IDs have been found return an empty list.
        if not descriptor_ids:
            return []

        # Find all PubMed citations associated with the MeSH descriptors found
        # prior.
        query = session.query(ModelCitation)

        # Filter citations by associated mesh-descriptors.
        query = query.join(ModelCitation.descriptors)
        query = query.filter(ModelDescriptor.descriptor_id.in_(descriptor_ids))

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

        # Limit query to fields requested in the GraphQL query.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelCitation,
        )

        objs = query.all()

        return objs
