# coding=utf-8

import sqlalchemy.orm
from sqlalchemy import func as sqlalchemy_func

from ffgraphql.types.ct_primitives import ModelFacilityCanonical


def add_canonical_facility_fix_filter(
    query: sqlalchemy.orm.Query,
) -> sqlalchemy.orm.Query:
    """ Adds a filter to the `query` to exclude canonical facilities where
        the name of the facility is the same as the facility's city, state,
        country, etc cause that indicates a facility that couldn't be matched
        and fell back to the encompassing area.

    Args:
        query (sqlalchemy.orm.Query): The query on which to add the filter.

    Returns:
        sqlalchemy.orm.Query: The updated query.
    """

    # Define coalescence function on the canonical facility fields to
    # preclude NULL values from yielding NULL results and therefore invalid
    # comparisons.
    func_coal_name = sqlalchemy_func.coalesce(
        ModelFacilityCanonical.name, ""
    )
    func_coal_country = sqlalchemy_func.coalesce(
        ModelFacilityCanonical.country, ""
    )
    func_coal_aal1 = sqlalchemy_func.coalesce(
        ModelFacilityCanonical.administrative_area_level_1, ""
    )
    func_coal_locality = sqlalchemy_func.coalesce(
        ModelFacilityCanonical.locality, ""
    )
    func_coal_sublocality = sqlalchemy_func.coalesce(
        ModelFacilityCanonical.sublocality, ""
    )
    func_coal_sl1 = sqlalchemy_func.coalesce(
        ModelFacilityCanonical.sublocality_level_1, ""
    )
    func_coal_neighborhood = sqlalchemy_func.coalesce(
        ModelFacilityCanonical.neighborhood, ""
    )

    query = query.filter(
        sqlalchemy.and_(
            func_coal_name != func_coal_country,
            func_coal_name != func_coal_locality,
            func_coal_name != func_coal_aal1,
            func_coal_name != func_coal_sublocality,
            func_coal_name != func_coal_sl1,
            func_coal_name != func_coal_neighborhood,
        )
    )

    return query
