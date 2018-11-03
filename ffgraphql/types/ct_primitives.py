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
from fform.orm_ct import Enrollment as ModelEnrollment
from fform.orm_ct import StudyDesignInfo as ModelStudyDesignInfo
from fform.orm_ct import Contact as ModelContact
from fform.orm_ct import Person as ModelPerson
from fform.orm_ct import Investigator as ModelInvestigator
from fform.orm_ct import StudyInvestigator as ModelStudyInvestigator
from fform.orm_ct import LocationInvestigator as ModelLocationInvestigator
from fform.orm_ct import StudyOutcome as ModelStudyOutcome
from fform.orm_ct import ProtocolOutcome as ModelProtocolOutcome
from fform.orm_ct import StudyReference as ModelStudyReference
from fform.orm_ct import Reference as ModelReference
from fform.orm_ct import ActualType as EnumActualType
from fform.orm_ct import OverallStatusType as EnumOverallStatus
from fform.orm_ct import InterventionType as EnumIntervention
from fform.orm_ct import PhaseType as EnumPhase
from fform.orm_ct import StudyType as EnumStudy
from fform.orm_ct import GenderType as EnumGender
from fform.orm_ct import MeshTermType as EnumMeshTerm
from fform.orm_ct import SamplingMethodType as EnumSamplingMethod
from fform.orm_ct import RecruitmentStatusType as EnumRecruitmentStatus
from fform.orm_ct import RoleType as EnumRoleType
from fform.orm_ct import OutcomeType as EnumOutcomeType
from fform.orm_ct import ReferenceType as EnumReferenceType


TypeEnumOverallStatus = graphene.Enum.from_enum(EnumOverallStatus)
TypeEnumPhase = graphene.Enum.from_enum(EnumPhase)
TypeEnumStudy = graphene.Enum.from_enum(EnumStudy)
TypeEnumRole = graphene.Enum.from_enum(EnumRoleType)
TypeEnumRecruitmentStatus = graphene.Enum.from_enum(EnumRecruitmentStatus)
TypeEnumMeshTerm = graphene.Enum.from_enum(EnumMeshTerm)
TypeEnumGender = graphene.Enum.from_enum(EnumGender)
TypeEnumSamplingMethod = graphene.Enum.from_enum(EnumSamplingMethod)
TypeActualType = graphene.Enum.from_enum(EnumActualType)
TypeEnumIntervention = graphene.Enum.from_enum(EnumIntervention)
TypeEnumOutcome = graphene.Enum.from_enum(EnumOutcomeType)
TypeEnumReference = graphene.Enum.from_enum(EnumReferenceType)


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


class TypeContact(SQLAlchemyObjectType):
    class Meta:
        model = ModelContact


class TypePerson(SQLAlchemyObjectType):
    class Meta:
        model = ModelPerson


class TypeInvestigator(SQLAlchemyObjectType):

    role = TypeEnumRole()

    class Meta:
        model = ModelInvestigator
        exclude_fields = ["role"]

    def resolve_role(self, info, **kwargs):
        return self.role


class TypeStudyInvestigator(SQLAlchemyObjectType):
    class Meta:
        model = ModelStudyInvestigator


class TypeLocationInvestigator(SQLAlchemyObjectType):
    class Meta:
        model = ModelLocationInvestigator


class TypeLocation(SQLAlchemyObjectType):

    status = TypeEnumRecruitmentStatus()

    class Meta:
        model = ModelLocation
        exclude_fields = ['status']

    def resolve_status(self, info, **kwargs):
        return self.status


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

    mesh_term_type = TypeEnumMeshTerm()

    class Meta:
        model = ModelStudyMeshTerm
        exclude_fields = [
            "mesh_term_type",
        ]

    def resolve_mesh_term_type(self, info, **kwargs):
        return self.mesh_term_type


class TypeEligibility(SQLAlchemyObjectType):

    gender = TypeEnumGender()

    sampling_method = TypeEnumSamplingMethod()

    class Meta:
        model = ModelEligibility
        exclude_fields = ["gender", "sampling_method"]

    def resolve_gender(self, info, **kwargs):
        return self.gender

    def resolve_sampling_method(self, info, **kwargs):
        return self.sampling_method


class TypeStudyFacility(SQLAlchemyObjectType):
    class Meta:
        model = ModelStudyFacility


class TypeEnrollment(SQLAlchemyObjectType):

    enrollment_type = TypeActualType()

    class Meta:
        model = ModelEnrollment
        exclude_fields = ["enrollment_type"]

    def resolve_enrollment_type(self, info, **kwargs):
        return self.enrollment_type


class TypeStudyDesignInfo(SQLAlchemyObjectType):

    class Meta:
        model = ModelStudyDesignInfo


class TypeStudyOutcome(SQLAlchemyObjectType):

    outcome_type = TypeEnumOutcome()

    class Meta:
        model = ModelStudyOutcome
        exclude_fields = ["outcome_type"]

    def resolve_outcome_type(self, info, **kwargs):
        return self.outcome_type


class TypeProtocolOutcome(SQLAlchemyObjectType):

    class Meta:
        model = ModelProtocolOutcome


class TypeStudyReference(SQLAlchemyObjectType):

    reference_type = TypeEnumReference()

    class Meta:
        model = ModelStudyReference
        exclude_fields = ["reference_type"]

    def resolve_reference_type(self, info, **kwargs):
        return self.reference_type


class TypeReference(SQLAlchemyObjectType):

    class Meta:
        model = ModelReference


class TypeEnumOrder(graphene.Enum):

    ASC = "ASC"
    DESC = "DESC"
