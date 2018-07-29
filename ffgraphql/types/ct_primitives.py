# coding=utf-8

from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_ct import Study as ModelStudy
from fform.orm_ct import MeshTerm as ModelMeshTerm
from fform.orm_ct import Location as ModelLocation
from fform.orm_ct import Facility as ModelFacility
from fform.orm_ct import Intervention as ModelIntervention
from fform.orm_ct import OverallStatusType as EnumOverallStatus
from fform.orm_ct import InterventionType as EnumIntervention
from fform.orm_ct import PhaseType as EnumPhase
from fform.orm_ct import StudyType as EnumStudy
from fform.orm_mt import Descriptor as ModelDescriptor
from fform.orm_mt import TreeNumber as ModelTreeNumber


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


class TypeIntervention(SQLAlchemyObjectType):
    class Meta:
        model = ModelIntervention


class TypeDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelDescriptor


class TypeTreeNumber(SQLAlchemyObjectType):
    class Meta:
        model = ModelTreeNumber
