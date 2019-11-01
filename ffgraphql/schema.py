# coding=utf-8

import graphene

from ffgraphql.types.ct_primitives import (
    TypeEnumOverallStatus,
    TypeStudy,
    TypeLocation,
    TypeFacility,
    TypeFacilityCanonical,
    TypeIntervention,
    TypeCondition,
    TypeStudyDescriptor,
    TypeEligibility,
    TypeStudyFacility,
    TypeEnrollment,
    TypeStudyDesignInfo,
    TypeContact,
    TypePerson,
    TypeInvestigator,
    TypeStudyInvestigator,
    TypeStudyOutcome,
    TypeProtocolOutcome,
    TypeStudyReference,
    TypeReference,
    TypeStudyIntervention,
    TypeInterventionArmGroup,
    TypeStudyDates,
    TypeArmGroup,
    TypeEnumOrder,
    TypeEnumIntervention,
    TypeEnumPhase,
    TypeEnumStudy,
    TypeEnumGender,
    TypeEnumMeshTerm,
    TypeEnumSamplingMethod,
    TypeEnumRecruitmentStatus,
    TypeEnumRole,
    TypeEnumOutcome,
    TypeEnumReference,
)
from ffgraphql.types.mt_primitives import (
    TypeTreeNumber,
    TypeThesaurusId,
    TypeTerm,
    TypeTermThesaurusId,
    TypeRelatedRegistryNumber,
    TypeConcept,
    TypeConceptRelatedRegistryNumber,
    TypeConceptRelatedConcept,
    TypeConceptTerm,
    TypeQualifier,
    TypeQualifierConcept,
    TypeQualifierTreeNumber,
    TypePreviousIndexing,
    TypeEnumEntryCombination,
    TypeDescriptor,
    TypeDescriptorEntryCombination,
    TypeDescriptorConcept,
    TypeDescriptorPreviousIndexing,
    TypeDescriptorAllowableQualifier,
    TypeDescriptorTreeNumber,
    TypeDescriptorPharmacologicalActionDescriptor,
    TypeDescriptorRelatedDescriptor,
    TypeSource,
    TypeSupplemental,
    TypeSupplementalHeadingMappedTo,
    TypeSupplementalIndexingInformation,
    TypeSupplementalConcept,
    TypeSupplementalPreviousIndexing,
    TypeSupplementalPharmacologicalActionDescriptor,
    TypeSupplementalSource,
    TypeDescriptorSynonym,
    TypeDescriptorDefinition,
)
from ffgraphql.types.pubmed_primitives import (
    TypeCitation,
    TypeArticle,
    TypeJournalInfo,
    TypeJournal,
    TypeCitationDescriptorQualifier,
    TypeAffiliationCanonical,
    TypeArticleAuthorAffiliation,
    TypeEnumJournalIssn,
)
from ffgraphql.types.app_primitives import (
    TypeUser,
    TypeSearch,
    TypeUserSearch,
    TypeSearchDescriptor,
    TypeUserStudy,
    TypeUserCitation,
)
from ffgraphql.types.mp_primitives import (
    TypeHealthTopicGroupClass,
    TypeHealthTopicGroup,
    TypeBodyPart,
    TypeAlsoCalled,
    TypePrimaryInstitute,
    TypeSeeReference,
    TypeHealthTopicHealthTopicGroup,
    TypeHealthTopicAlsoCalled,
    TypeHealthTopicDescriptor,
    TypeHealthTopicRelatedHealthTopic,
    TypeHealthTopicSeeReference,
    TypeHealthTopicBodyPart,
    TypeHealthTopic,
)
from ffgraphql.types.studies import TypeStudies
from ffgraphql.types.descriptors import TypeDescriptors
from ffgraphql.types.citations import TypeCitations
from ffgraphql.types.users import TypeUsers
from ffgraphql.types.searches import TypeSearches
from ffgraphql.types.health_topics import (
    TypeHealthTopics,
    TypeHealthTopicGroups,
    TypeBodyParts,
)
from ffgraphql.types.studies_stats import (
    TypeCountStudiesCountry,
    TypeCountStudiesOverallStatus,
    TypeCountStudiesFacility,
    TypeCountStudiesFacilityDescriptor,
    TypeCountStudiesDescriptor,
    TypeDateRange,
    TypeAgeRange,
    TypeStudiesStats,
)
from ffgraphql.types.citations_stats import (
    TypeCountCitationsCountry,
    TypeCountCitationsAffiliation,
    TypeCitationsStats,
)
from ffgraphql.mutations.users import (
    MutationUserUpsert,
    MutationUserDelete,
    MutationUserStudyUpsert,
    MutationUserCitationUpsert,
    MutationUserStudyDelete,
    MutationUserCitationDelete,
)
from ffgraphql.mutations.searches import (
    MutationSearchUpsert,
    MutationSearchDelete,
)


class Query(graphene.ObjectType):

    studies_stats = graphene.Field(
        type=TypeStudiesStats,
        description="Clinical-trial study-related statistics."
    )

    studies = graphene.Field(
        type=TypeStudies,
        description="Clinical-trials studies.",
    )

    descriptors = graphene.Field(
        type=TypeDescriptors,
        description="MeSH descriptors.",
    )

    citations = graphene.Field(
        type=TypeCitations,
        description="PubMed citations.",
    )

    citations_stats = graphene.Field(
        type=TypeCitationsStats,
        description="PubMed citation-related statistics.",
    )

    users = graphene.Field(type=TypeUsers, description="Application users.")

    searches = graphene.Field(type=TypeSearches, description="User searches.")

    health_topics = graphene.Field(
        type=TypeHealthTopics,
        description="MedlinePlus health-topics.",
    )

    health_topic_groups = graphene.Field(
        type=TypeHealthTopicGroups,
        description="MedlinePlus health-topic groups.",
    )

    body_parts = graphene.Field(
        type=TypeBodyParts,
        description="MedlinePlus body-parts.",
    )

    @staticmethod
    def resolve_studies_stats(args, info):
        return TypeStudiesStats

    @staticmethod
    def resolve_studies(args, info):
        return TypeStudies

    @staticmethod
    def resolve_descriptors(args, info):
        return TypeDescriptors

    @staticmethod
    def resolve_citations(args, info):
        return TypeCitations

    @staticmethod
    def resolve_citations_stats(args, info):
        return TypeCitationsStats

    @staticmethod
    def resolve_users(args, info):
        return TypeUsers

    @staticmethod
    def resolve_searches(args, info):
        return TypeSearches

    @staticmethod
    def resolve_health_topics(args, info):
        return TypeHealthTopics

    @staticmethod
    def resolve_health_topic_groups(args, info):
        return TypeHealthTopicGroups

    @staticmethod
    def resolve_body_parts(args, info):
        return TypeBodyParts


class Mutation(graphene.ObjectType):
    """GraphQL mutations."""

    upsert_user = MutationUserUpsert.Field()
    delete_user = MutationUserDelete.Field()

    upsert_search = MutationSearchUpsert.Field()
    delete_search = MutationSearchDelete.Field()

    upsert_user_study = MutationUserStudyUpsert.Field()
    upsert_user_citation = MutationUserCitationUpsert.Field()

    delete_user_study = MutationUserStudyDelete.Field()
    delete_user_citation = MutationUserCitationDelete.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    types=[
        # Clinical-trial primitives.
        TypeEnumOverallStatus,
        TypeStudy,
        TypeLocation,
        TypeFacility,
        TypeFacilityCanonical,
        TypeIntervention,
        TypeCondition,
        TypeStudyDescriptor,
        TypeEligibility,
        TypeStudyFacility,
        TypeEnrollment,
        TypeStudyDesignInfo,
        TypeContact,
        TypePerson,
        TypeInvestigator,
        TypeStudyInvestigator,
        TypeStudyOutcome,
        TypeProtocolOutcome,
        TypeStudyReference,
        TypeReference,
        TypeArmGroup,
        TypeStudyIntervention,
        TypeInterventionArmGroup,
        TypeStudyDates,
        TypeEnumOrder,
        TypeEnumIntervention,
        TypeEnumPhase,
        TypeEnumStudy,
        TypeEnumGender,
        TypeEnumMeshTerm,
        TypeEnumSamplingMethod,
        TypeEnumRecruitmentStatus,
        TypeEnumRole,
        TypeEnumOutcome,
        TypeEnumReference,
        # MeSH term primitives.
        TypeTreeNumber,
        TypeThesaurusId,
        TypeTerm,
        TypeTermThesaurusId,
        TypeRelatedRegistryNumber,
        TypeConcept,
        TypeConceptRelatedRegistryNumber,
        TypeConceptRelatedConcept,
        TypeConceptTerm,
        TypeQualifier,
        TypeQualifierConcept,
        TypeQualifierTreeNumber,
        TypePreviousIndexing,
        TypeEnumEntryCombination,
        TypeDescriptor,
        TypeDescriptorEntryCombination,
        TypeDescriptorConcept,
        TypeDescriptorPreviousIndexing,
        TypeDescriptorAllowableQualifier,
        TypeDescriptorTreeNumber,
        TypeDescriptorPharmacologicalActionDescriptor,
        TypeDescriptorRelatedDescriptor,
        TypeSource,
        TypeSupplemental,
        TypeSupplementalHeadingMappedTo,
        TypeSupplementalIndexingInformation,
        TypeSupplementalConcept,
        TypeSupplementalPreviousIndexing,
        TypeSupplementalPharmacologicalActionDescriptor,
        TypeSupplementalSource,
        TypeDescriptorSynonym,
        TypeDescriptorDefinition,
        # PubMed primitives.
        TypeCitation,
        TypeArticle,
        TypeJournalInfo,
        TypeJournal,
        TypeCitationDescriptorQualifier,
        TypeAffiliationCanonical,
        TypeArticleAuthorAffiliation,
        TypeEnumJournalIssn,
        # App primitives.
        TypeUser,
        TypeSearch,
        TypeUserSearch,
        TypeSearchDescriptor,
        TypeUserStudy,
        TypeUserCitation,
        # MedlinePlus primitives.
        TypeHealthTopicGroupClass,
        TypeHealthTopicGroup,
        TypeBodyPart,
        TypeAlsoCalled,
        TypePrimaryInstitute,
        TypeSeeReference,
        TypeHealthTopicHealthTopicGroup,
        TypeHealthTopicAlsoCalled,
        TypeHealthTopicDescriptor,
        TypeHealthTopicRelatedHealthTopic,
        TypeHealthTopicSeeReference,
        TypeHealthTopicBodyPart,
        TypeHealthTopic,
        # Clinical trials studies.
        TypeStudies,
        # MeSH descriptors.
        TypeDescriptors,
        # PubMed citations.
        TypeCitations,
        # Application users.
        TypeUsers,
        # Application searches.
        TypeSearches,
        # MedlinePlus health-topics.
        TypeHealthTopics,
        TypeHealthTopicGroups,
        TypeBodyParts,
        # Clinical trials study statistics.
        TypeCountStudiesCountry,
        TypeCountStudiesOverallStatus,
        TypeCountStudiesFacility,
        TypeCountStudiesFacilityDescriptor,
        TypeCountStudiesDescriptor,
        TypeDateRange,
        TypeAgeRange,
        TypeStudiesStats,
        # PubMed citation statistics.
        TypeCountCitationsCountry,
        TypeCountCitationsAffiliation,
        TypeCitationsStats,
    ],
)
