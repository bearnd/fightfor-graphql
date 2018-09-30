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
from fform.orm_ct import MeshTermType as EnumMeshTerm


TypeEnumOverallStatus = graphene.Enum.from_enum(EnumOverallStatus)

TypeEnumPhase = graphene.Enum.from_enum(EnumPhase)

TypeEnumStudy = graphene.Enum.from_enum(EnumStudy)


class TypeStudy(SQLAlchemyObjectType):

    overall_status = TypeEnumOverallStatus()
    phase = TypeEnumPhase()
    study_type = TypeEnumStudy()

    class Meta:
        model = ModelStudy
        exclude_fields = [
            "overall_status",
            "phase",
            "study_type",
        ]

    def resolve_overall_status(self, info, **kwargs):
        return self.overall_status

    def resolve_phase(self, info, **kwargs):
        return self.phase

    def resolve_study_type(self, info, **kwargs):
        return self.study_type


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


TypeEnumGender = graphene.Enum.from_enum(EnumGender)


class TypeEligibility(SQLAlchemyObjectType):

    gender = TypeEnumGender()

    class Meta:
        model = ModelEligibility
        exclude_fields = ["gender"]

    def resolve_gender(self, info, **kwargs):
        return self.gender


class TypeStudyFacility(SQLAlchemyObjectType):
    class Meta:
        model = ModelStudyFacility


class TypeEnumOrder(graphene.Enum):

    ASC = "ASC"
    DESC = "DESC"


TypeEnumIntervention = graphene.Enum.from_enum(EnumIntervention)



TypeEnumMeshTerm = graphene.Enum.from_enum(EnumMeshTerm)
