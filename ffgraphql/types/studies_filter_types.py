# coding=utf-8

import operator

import graphene
import sqlalchemy
from fform.orm_ct import Study as StudyModel


class OrderType(graphene.Enum):
    ASC = "ASC"
    DESC = "DESC"


class FilterOperatorNumericType(graphene.Enum):
    EQ = operator.eq
    NE = operator.ne
    GT = operator.gt
    LT = operator.lt
    LE = operator.le
    GE = operator.ge


class StudyFilterType(graphene.InputObjectType):

    field = graphene.Enum(
        "StudyFieldType",
        sqlalchemy.inspect(StudyModel)
    )
    field = graphene.String(description="The field to filter by.")

    operator = graphene.Field(FilterOperatorType)

    value = graphene.String()


class StudyFilterInt(graphene.InputObjectType):
    operator = graphene.Field(
        type=FilterOperatorNumericType,
        description=("The numerical operator to apply in the filtering "
                     "operation."),
        required=True,
    )



class StudyFilterStudyId(graphene.InputObjectType):



    value = graphene.Int(required=True)


class FilterStudyOverallStatus(graphene.InputObjectType):

