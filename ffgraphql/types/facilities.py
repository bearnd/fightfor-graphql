# coding=utf-8

from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_ct import Facility as FacilityModel


class FacilityType(SQLAlchemyObjectType):
    class Meta:
        model = FacilityModel
