# coding=utf-8

import graphene

from ffgraphql.types.ct_primitives import (
    TypeEnumOverallStatus,
    TypeStudy,
    TypeMeshTerm,
    TypeLocation,
    TypeFacility,
    TypeFacilityCanonical,
    TypeIntervention,
    TypeCondition,
    TypeStudyMeshTerm,
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
    TypeDescriptor,
    TypeTreeNumber,
    TypeDescriptorSynonym,
    TypeConcept,
    TypeQualifier,
)
from ffgraphql.types.pubmed_primitives import (
    TypeCitation,
    TypeArticle,
    TypeJournalInfo,
    TypeJournal,
    TypeChemical,
    TypePubMedDescriptor,
    TypePubMedQualifier,
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
)
from ffgraphql.types.studies import TypeStudies
from ffgraphql.types.descriptors import TypeDescriptors
from ffgraphql.types.citations import TypeCitations
from ffgraphql.types.users import TypeUsers
from ffgraphql.types.searches import TypeSearches
from ffgraphql.types.studies_stats import (
    TypeCountStudiesCountry,
    TypeCountStudiesOverallStatus,
    TypeCountStudiesFacility,
    TypeCountStudiesFacilityMeshTerm,
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


class Mutation(graphene.ObjectType):
    """GraphQL mutations."""

    upsert_user = MutationUserUpsert.Field()
    delete_user = MutationUserDelete.Field()

    upsert_search = MutationSearchUpsert.Field()
    delete_search = MutationSearchDelete.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    types=[
        # Clinical-trial primitives.
        TypeEnumOverallStatus,
        TypeStudy,
        TypeMeshTerm,
        TypeLocation,
        TypeFacility,
        TypeFacilityCanonical,
        TypeIntervention,
        TypeCondition,
        TypeStudyMeshTerm,
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
        TypeDescriptor,
        TypeTreeNumber,
        TypeDescriptorSynonym,
        TypeConcept,
        TypeQualifier,
        # PubMed primitives.
        TypeCitation,
        TypeArticle,
        TypeJournalInfo,
        TypeJournal,
        TypeChemical,
        TypePubMedDescriptor,
        TypePubMedQualifier,
        TypeCitationDescriptorQualifier,
        TypeAffiliationCanonical,
        TypeArticleAuthorAffiliation,
        TypeEnumJournalIssn,
        # App primitives.
        TypeUser,
        TypeSearch,
        TypeUserSearch,
        TypeSearchDescriptor,
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
        # Clinical trials study statistics.
        TypeCountStudiesCountry,
        TypeCountStudiesOverallStatus,
        TypeCountStudiesFacility,
        TypeCountStudiesFacilityMeshTerm,
        TypeDateRange,
        TypeAgeRange,
        TypeStudiesStats,
        # PubMed citation statistics.
        TypeCountCitationsCountry,
        TypeCountCitationsAffiliation,
        TypeCitationsStats,
    ],
)
