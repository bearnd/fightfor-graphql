# coding=utf-8

from typing import List, Optional

import sqlalchemy.orm
import graphene
from sqlalchemy import func as sqlalchemy_func

from ffgraphql.types.pubmed_primitives import ModelCitation
from ffgraphql.types.pubmed_primitives import ModelArticleAuthorAffiliation
from ffgraphql.types.pubmed_primitives import ModelAffiliationCanonical
from ffgraphql.types.pubmed_primitives import TypeAffiliationCanonical
from ffgraphql.types.pubmed_primitives import ModelCitationDescriptorQualifier
from ffgraphql.types.mt_primitives import ModelQualifier
from ffgraphql.types.mt_primitives import TypeQualifier
from ffgraphql.utils import extract_requested_fields
from ffgraphql.utils import apply_requested_fields


class TypeCountCitationsCountry(graphene.ObjectType):
    """Graphene type representing a single result of an aggregation operation
    calculating the number of citations by country."""

    country = graphene.String(
        description=("The country in which the citation affiliations are "
                     "located.")
    )

    count_citations = graphene.Int(description="The number of citations.")


class TypeCountCitationsAffiliation(graphene.ObjectType):
    """Graphene type representing a single result of an aggregation operation
    calculating the number of citations by canonical affiliation."""

    affiliation_canonical = graphene.Field(
        type=TypeAffiliationCanonical,
        description="The canonical affiliation to which the citations refer."
    )

    count_citations = graphene.Int(description="The number of citations.")


class TypeCountCitationsQualifier(graphene.ObjectType):
    """Graphene type representing a single result of an aggregation operation
    calculating the number of citations by MeSH qualifier."""

    qualifier = graphene.Field(
        type=TypeQualifier,
        description="The MeSH qualifier to which the citations refer."
    )

    count_citations = graphene.Int(description="The number of citations.")


class TypeCitationsStats(graphene.ObjectType):

    count_citations_by_country = graphene.List(
        of_type=TypeCountCitationsCountry,
        citation_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True,
        ),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    count_citations_by_affiliation = graphene.List(
        of_type=TypeCountCitationsAffiliation,
        citation_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True,
        ),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    count_citations_by_qualifier = graphene.List(
        of_type=TypeCountCitationsQualifier,
        citation_ids=graphene.Argument(
            type=graphene.List(of_type=graphene.Int),
            required=True,
        ),
        limit=graphene.Argument(type=graphene.Int, required=False),
    )

    @staticmethod
    def resolve_count_citations_by_country(
        args: dict,
        info: graphene.ResolveInfo,
        citation_ids: List[int],
        limit: Optional[int] = None,
    ) -> List[TypeCountCitationsCountry]:
        """Creates a list of `TypeCountCitationsCountry` objects with the number
        of citations per country.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            citation_ids (List[int]): A list of citation IDs.
            limit (Optional[int]): The number of results to return. Defaults to
                `None` in which case all results are returned.

        Returns:
             list[TypeCountCitationsCountry]: The list of
                `TypeCountCitationsCountry` objects with the results of the
                aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(citations.citation_id)` function.
        func_count_citations = sqlalchemy_func.count(
            sqlalchemy_func.distinct(ModelCitation.citation_id),
        )

        # Query out the count of citations by country.
        query = session.query(
            ModelAffiliationCanonical.country,
            func_count_citations,
        )  # type: sqlalchemy.orm.Query
        query = query.join(
            ModelArticleAuthorAffiliation,
            ModelAffiliationCanonical.affiliation_canonical_id ==
            ModelArticleAuthorAffiliation.affiliation_canonical_id,
        )
        query = query.join(
            ModelCitation,
            ModelCitation.article_id ==
            ModelArticleAuthorAffiliation.article_id,
        )
        query = query.filter(ModelCitation.citation_id.in_(citation_ids))
        # Group by citation country.
        query = query.group_by(ModelAffiliationCanonical.country)
        # Order by the number of studies.
        query = query.order_by(func_count_citations.desc())

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        results = query.all()

        # Wrap the results of the aggregation in `TypeCountCitationsCountry`
        # objects.
        objs = [
            TypeCountCitationsCountry(
                country=result[0],
                count_citations=result[1]
            ) for result in results
        ]

        return objs

    @staticmethod
    def resolve_count_citations_by_affiliation(
        args: dict,
        info: graphene.ResolveInfo,
        citation_ids: List[int],
        limit: Optional[int] = None,
    ) -> List[TypeCountCitationsAffiliation]:
        """Creates a list of `TypeCountCitationsAffiliation` objects with the
        number of citations per affiliation.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            citation_ids (List[int]): A list of citation IDs.
            limit (Optional[int]): The number of results to return. Defaults to
                `None` in which case all results are returned.

        Returns:
             list[TypeCountCitationsAffiliation]: The list of
                `TypeCountCitationsAffiliation` objects with the results of the
                aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(citations.citation_id)` function.
        func_count_citations = sqlalchemy_func.count(
            sqlalchemy_func.distinct(ModelCitation.citation_id),
        )

        # Query out the count of citations by country.
        query = session.query(
            ModelAffiliationCanonical,
            func_count_citations,
        )  # type: sqlalchemy.orm.Query
        query = query.join(
            ModelArticleAuthorAffiliation,
            ModelAffiliationCanonical.affiliation_canonical_id ==
            ModelArticleAuthorAffiliation.affiliation_canonical_id,
        )
        query = query.join(
            ModelCitation,
            ModelCitation.article_id ==
            ModelArticleAuthorAffiliation.article_id,
        )
        query = query.filter(ModelCitation.citation_id.in_(citation_ids))
        # Group by citation country.
        query = query.group_by(
            ModelAffiliationCanonical.affiliation_canonical_id,
        )
        # Order by the number of studies.
        query = query.order_by(func_count_citations.desc())

        # Extract the fields requested in the GraphQL query.
        fields = extract_requested_fields(
            info=info,
            fields=info.field_asts,
            do_convert_to_snake_case=True,
        )["count_citations_by_affiliation"]["affiliation_canonical"]

        # Limit query to `AffiliationCanonical` fields requested in the GraphQL
        # query.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelAffiliationCanonical,
            fields={"affiliation": fields},
        )

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        results = query.all()

        # Wrap the results of the aggregation in `TypeCountCitationsCountry`
        # objects.
        objs = [
            TypeCountCitationsAffiliation(
                affiliation_canonical=result[0],
                count_citations=result[1]
            ) for result in results
        ]

        return objs

    @staticmethod
    def resolve_count_citations_by_qualifier(
        args: dict,
        info: graphene.ResolveInfo,
        citation_ids: List[int],
        limit: Optional[int] = None,
    ) -> List[TypeCountCitationsQualifier]:
        """Creates a list of `TypeCountCitationsQualifier` objects with the
        number of citations per qualifier.

        Args:
            args (dict): The resolver arguments.
            info (graphene.ResolveInfo): The resolver info.
            citation_ids (List[int]): A list of citation IDs.
            limit (Optional[int]): The number of results to return. Defaults to
                `None` in which case all results are returned.

        Returns:
             list[TypeCountCitationsQualifier]: The list of
                `TypeCountCitationsQualifier` objects with the results of the
                aggregation.
        """

        # Retrieve the session out of the context as the `get_query` method
        # automatically selects the model.
        session = info.context.get("session")  # type: sqlalchemy.orm.Session

        # Define the `COUNT(citations.citation_id)` function.
        func_count_citations = sqlalchemy_func.count(
            sqlalchemy_func.distinct(
                ModelCitationDescriptorQualifier.citation_id
            ),
        )

        # Query out the count of citations by country.
        query = session.query(
            ModelQualifier,
            func_count_citations,
        )  # type: sqlalchemy.orm.Query
        query = query.join(
            ModelCitationDescriptorQualifier,
            ModelCitationDescriptorQualifier.qualifier_id ==
            ModelQualifier.qualifier_id,
        )
        query = query.filter(
            ModelCitationDescriptorQualifier.citation_id.in_(citation_ids),
        )
        # Group by qualifier.
        query = query.group_by(
            ModelQualifier.qualifier_id,
        )
        # Order by the number of studies.
        query = query.order_by(func_count_citations.desc())

        # Extract the fields requested in the GraphQL query.
        fields = extract_requested_fields(
            info=info,
            fields=info.field_asts,
            do_convert_to_snake_case=True,
        )["count_citations_by_qualifier"]["qualifier"]

        # Limit query to `ModelQualifier` fields requested in the GraphQL
        # query.
        query = apply_requested_fields(
            info=info,
            query=query,
            orm_class=ModelQualifier,
            fields={"qualifier": fields},
        )

        # Apply limit (if defined).
        if limit:
            query = query.limit(limit=limit)

        results = query.all()

        # Wrap the results of the aggregation in `TypeCountCitationsQualifier`
        # objects.
        objs = [
            TypeCountCitationsQualifier(
                qualifier=result[0],
                count_citations=result[1]
            ) for result in results
        ]

        return objs
