# coding=utf-8

from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_app import User as ModelUser
from fform.orm_app import Search as ModelSearch
from fform.orm_app import UserSearch as ModelUserSearch
from fform.orm_app import SearchDescriptor as ModelSearchDescriptor
from fform.orm_app import UserStudy as ModelUserStudy
from fform.orm_app import UserCitation as ModelUserCitation

from ffgraphql.types.ct_primitives import TypeEnumGender


class TypeUser(SQLAlchemyObjectType):
    class Meta:
        model = ModelUser


class TypeSearch(SQLAlchemyObjectType):

    gender = TypeEnumGender()

    class Meta:
        model = ModelSearch
        exclude_fields = ["gender"]

    def resolve_gender(self, info, **kwargs):
        return self.gender


class TypeUserSearch(SQLAlchemyObjectType):
    class Meta:
        model = ModelUserSearch


class TypeSearchDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelSearchDescriptor


class TypeUserStudy(SQLAlchemyObjectType):
    class Meta:
        model = ModelUserStudy


class TypeUserCitation(SQLAlchemyObjectType):
    class Meta:
        model = ModelUserCitation
