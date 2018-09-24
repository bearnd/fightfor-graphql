# coding=utf-8

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_ct import Study as ModelStudy
from fform.orm_ct import MeshTerm as ModelMeshTerm
from fform.orm_ct import Location as ModelLocation
from fform.orm_ct import Facility as ModelFacility
from fform.orm_ct import StudyFacility as ModelStudyFacility
from fform.orm_ct import FacilityCanonical as ModelFacilityCanonical
from fform.orm_ct import Intervention as ModelIntervention
from fform.orm_ct import Condition as ModelCondition
from fform.orm_ct import StudyMeshTerm as ModelStudyMeshTerm
from fform.orm_ct import Eligibility as ModelEligibility
from fform.orm_ct import OverallStatusType as EnumOverallStatus
from fform.orm_ct import InterventionType as EnumIntervention
from fform.orm_ct import PhaseType as EnumPhase
from fform.orm_ct import StudyType as EnumStudy
from fform.orm_ct import GenderType as EnumGender


class TypeEnumOrder(graphene.Enum):

    ASC = "ASC"
    DESC = "DESC"


class TypeStudy(SQLAlchemyObjectType):
    class Meta:
        model = ModelStudy


class TypeMeshTerm(SQLAlchemyObjectType):
    class Meta:
        model = ModelMeshTerm


class TypeLocation(SQLAlchemyObjectType):
    class Meta:
        model = ModelLocation


class TypeFacility(SQLAlchemyObjectType):
    class Meta:
        model = ModelFacility


class TypeFacilityCanonical(SQLAlchemyObjectType):
    class Meta:
        model = ModelFacilityCanonical


class TypeIntervention(SQLAlchemyObjectType):
    class Meta:
        model = ModelIntervention


class TypeCondition(SQLAlchemyObjectType):
    class Meta:
        model = ModelCondition


class TypeStudyMeshTerm(SQLAlchemyObjectType):
    class Meta:
        model = ModelStudyMeshTerm


class TypeEligibility(SQLAlchemyObjectType):
    class Meta:
        model = ModelEligibility


class TypeStudyFacility(SQLAlchemyObjectType):
    class Meta:
        model = ModelStudyFacility


TypeEnumOverallStatus = graphene.Enum.from_enum(EnumOverallStatus)

TypeEnumIntervention = graphene.Enum.from_enum(EnumIntervention)

TypeEnumPhase = graphene.Enum.from_enum(EnumPhase)

TypeEnumStudy = graphene.Enum.from_enum(EnumStudy)

TypeEnumGender = graphene.Enum.from_enum(EnumGender)
