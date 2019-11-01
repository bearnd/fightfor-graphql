# -*- coding: utf-8 -*-

from graphene_sqlalchemy import SQLAlchemyObjectType

from fform.orm_mp import (
    HealthTopicGroupClass as ModelHealthTopicGroupClass,
    HealthTopicGroup as ModelHealthTopicGroup,
    BodyPart as ModelBodyPart,
    AlsoCalled as ModelAlsoCalled,
    PrimaryInstitute as ModelPrimaryInstitute,
    SeeReference as ModelSeeReference,
    HealthTopicHealthTopicGroup as ModelHealthTopicHealthTopicGroup,
    HealthTopicAlsoCalled as ModelHealthTopicAlsoCalled,
    HealthTopicDescriptor as ModelHealthTopicDescriptor,
    HealthTopicRelatedHealthTopic as ModelHealthTopicRelatedHealthTopic,
    HealthTopicSeeReference as ModelHealthTopicSeeReference,
    HealthTopicBodyPart as ModelHealthTopicBodyPart,
    HealthTopic as ModelHealthTopic,
)


class TypeHealthTopicGroupClass(SQLAlchemyObjectType):
    class Meta:
        model = ModelHealthTopicGroupClass


class TypeHealthTopicGroup(SQLAlchemyObjectType):
    class Meta:
        model = ModelHealthTopicGroup


class TypeBodyPart(SQLAlchemyObjectType):
    class Meta:
        model = ModelBodyPart


class TypeAlsoCalled(SQLAlchemyObjectType):
    class Meta:
        model = ModelAlsoCalled


class TypePrimaryInstitute(SQLAlchemyObjectType):
    class Meta:
        model = ModelPrimaryInstitute


class TypeSeeReference(SQLAlchemyObjectType):
    class Meta:
        model = ModelSeeReference


class TypeHealthTopicHealthTopicGroup(SQLAlchemyObjectType):
    class Meta:
        model = ModelHealthTopicHealthTopicGroup


class TypeHealthTopicAlsoCalled(SQLAlchemyObjectType):
    class Meta:
        model = ModelHealthTopicAlsoCalled


class TypeHealthTopicDescriptor(SQLAlchemyObjectType):
    class Meta:
        model = ModelHealthTopicDescriptor


class TypeHealthTopicRelatedHealthTopic(SQLAlchemyObjectType):
    class Meta:
        model = ModelHealthTopicRelatedHealthTopic


class TypeHealthTopicSeeReference(SQLAlchemyObjectType):
    class Meta:
        model = ModelHealthTopicSeeReference


class TypeHealthTopicBodyPart(SQLAlchemyObjectType):
    class Meta:
        model = ModelHealthTopicBodyPart


class TypeHealthTopic(SQLAlchemyObjectType):
    class Meta:
        model = ModelHealthTopic
