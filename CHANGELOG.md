## Changelog

### v0.14.1

- Updated the `resolve_get_unique_cities`, `resolve_get_unique_states`, and `resolve_get_unique_countries` methods of the `TypeStudiesStats` class and replaced the repetitive code with a new `_query_unique_geographies` method.

### v0.14.0

Issue No. 277: Add Sentry to fightfor-graphql:

- Added encrypted Sentry DSN configuration to Ansible role.
- Added a new `sentry.py` module with a function to initialize the Sentry agent configured to work with Falcon and SQLAlchemy.
- Updated the `main` function of the `ffgraphql.py` module to initialize the Sentry agent.

Issue No. 86: `StudiesListComponent` pagination returns incorrect number of studies when filters are in effect:

- Updated the `_apply_query_filters` method of the `TypeStudies` class to only join-load facilities once if either facility IDs or geographical filters have been applied.
- Updated the `resolve_filter` method of the `TypeStudies` class to only execute the `apply_requested_fields` function if no LIMIT or OFFSET directives are to be applied as the joined-loads in `apply_requested_fields` cause incorrect pagination.

### v0.13.0

Issue No. 273: Expose MeSH primitives:

- Completely reworked the `mt_primitives.py` module and wrapped all available MeSH records classes as GraphQL types.
- Exposed all newly defined MeSH GraphQL types.

### v0.12.0

- Fixed bug in the `resolve_count` method of the `TypeStudies` class where the `COUNT` function was not using `DISTINCT`.

Issue No. 271: Expose MeSH descriptor definitions:

- Created a new `TypeDescriptorDefinition` class.
- Exposed the new `TypeDescriptorDefinition` class.
- Updated the `TypeDescriptor` class with a working resolver for the `descriptor_class` enumeration.
- Updated the `TypeDescriptorDefinition ` class with a working resolver for the `source` enumeration.

### v0.11.0

Issue No. 242: Add a canonical facility ID filter on the `filter` and `count` resolvers of the `TypeStudies` class:
- Updated the `_apply_query_filters` method of the `TypeStudies` class to include a `facility_canonical_ids` argument and filter on those IDs.
- Added the `filter` resolver and `resolve_filter` method of the `TypeStudies` class to permit filtering by canonical facility IDs.
- Added the `count` resolver and `resolve_count` method of the `TypeStudies` class to permit filtering by canonical facility IDs.

Issue No. 244: Add a new resolver to retrieve all unique canonical facilities out of a list of studies:
- Added a new `get_unique_canonical_facilities` resolver and `resolve_get_unique_canonical_facilities ` method to the `TypeStudiesStats` class to get the unique canonical facilities from a list of clinical-trials.

Issue No. 150:
- Updated the `TypeStudiesStats` class and its various resolver methods to filter out canonical facilities where the name of the facility matches the name of that facilitiy’s city, state, or country cause that’d indicate a fallback match.
- Updated the `TypeStudies` class and its various resolver methods to filter out canonical facilities where the name of the facility matches the name of that facilitiy’s city, state, or country cause that’d indicate a fallback match.

### v0.10.0

Issue No. 238: Add new resolver to count facilities based on a series of filters:
- Added a new `_apply_query_filters` method to the `TypeStudiesStats` class to apply the SQL query filters that were previously used in the `resolve_count_studies_by_facility` method.
- Added a new `count_facilities` resolver and `resolve_ count_facilities` method to the `TypeStudiesStats` class to count the facilities that can be returned by the `resolve_count_studies_by_facility` method when the same filters are applied.


### v0.9.1

- Fixed bug in the `resolve_count_studies_by_facility` of the `TypeStudiesStats` class where the ordering of the results was incorrectly performed against the studies instead of facilities.

### v0.9.0

Issue No. 232: Add filtering to `count_studies_by_facility` resolver:

- Fixed bug in different resolvers of the `TypeStudies` class where the geo-coordinates were types as integers instead of floats.
- Fixed bug in the different resolvers of `TypeStudiesStats` where a guard was added before study-filtering in case an empty list of study IDs was passed.
- Updated the `resolve_count_studies_by_facility` method and the `count_studies_by_facility` resolver to include and apply filtering to the query.
- Updated configuration variables.

Issue No. 233: Add `get_unique_descriptors` resolver to the `TypeStudiesStats` class:

- Updated descriptions and docstrings.
- Added a new `get_unique_descriptors` resolver and `resolve_get_unique_descriptors` method to the `TypeStudiesStats` class.

### v0.8.0

Issue No. 152: Implement top- and new-therapies card in `SearchResultsSummaryComponent`.

- Updated the `TypeStudiesStats` class and added a new attribute and method to calculate the number of studies by MeSH descriptor.
- Updated the `TypeStudiesStats` class and added a new attribute and method to find the latest MeSH descriptors for a group of studies.
- Updated the schema.

### v0.7.0

Issue No. 205: Update `fightfor-graphql` to new DB model:

- Increased gunicorn timeouts.
- Updated configuration variables.
- Updated the `resolve_search` method of the `TypeStudies` class porting it from using the now defunct `ModelMeshTerm` to using the `ModelDescriptor` class. The search is also based on MeSH descriptor IDs instead of names to increase performance.
- Updated the `resolve_search` method of the `TypeCitations` class porting it from using the now defunct `ModelPmDescriptor ` to using the `ModelDescriptor` class. The search is also based on MeSH descriptor IDs instead of names to increase performance.
- Updated the `TypeCitationsStats` class and the corresponding type classes to no longer use the defunct `ModelPmQualifier` and `ModelPmDescriptor` classes and instead use the `ModelQualifier` and `ModelDescriptor` classes.
- Updated the `TypeStudiesStats` class and the corresponding type classes to no longer use the defunct `ModelMeshTerm` and `ModelStudyMeshTerm` classes and instead use the `ModelDescriptor` and `ModelStudyDescriptor` classes.
- Removed defunct types.
- Removed the defunct `TypeMeshTerm` class and renamed/ported the `TypeStudyMeshTerm` as `TypeStudyDescriptor`.
- Updated schema.

Issue No. 176: Searches by MeSH terms operate in an OR manner instead of AND:

- Updated the `Makefile` to run unit-tests through `unittest`.
- Added a new `TypeDescriptorTreeNumber` primitive class.
- Updated the `resolve_search` method of the `TypeStudies` class and updated the study-search to operate on an AND fashion across the MeSH descriptors instead of an OR fashion.
- Updated the `resolve_search` method of the `TypeCitations` class and updated the citation-search to operate on an AND fashion across the MeSH descriptors instead of an OR fashion.

### v0.6.0

Issue No. 167: Add queries and mutations for saved studies/citations:

- Added new types for the `UserStudy` and `UserCitation` models.
- Added functions to retrieve a clinical trials study and a PubMed citation via their NCT and PubMed IDs.
- Added new mutation classes to upsert and delete `UserStudy` and `UserCitation` records.
- Updated the `resolve` method of the `MutationUserDelete` class to delete the `UserStudy` and `UserCitation` records linked to the user.

### v0.5.0

Issue No. 164: Implement `StudyComponent` to display the details of a clinical-trials study:

- Updated the Ansible role and added the installation of a local PostgreSQL server in the Vagrant VM.
- Updated the Vagrant configuraton and exposed the PostgreSQL server port.
- Refactored the `ct_primitives.py` module and added new types.

### v0.4.0

Issue No. 159: Add user and search mutations allowing for the creation, update, and deletion of corresponding records:

- Added a new `mutations` subpackage.
- Updated the `ResourceGraphQl` class and removed all the HTTP method handlers except for the POST as that’s the only one actively used.
- Updated the `ResourceGraphQl` and `ResourceGraphQlSqlAlchemy` classes to receive the application-configuration object which gets passed into the GraphQL resolver along with the decoded JWT token from the request context. Also removed the STDOUT redirect so that any logging occuring within the resolvers can be displayed.
- Updated the `on_post` method of the `ResourceGraphQl` class as errors were not being captured when the execution result contained both errors and data.
- Updated the instantiation of the `ResourceGraphQlSqlAlchemy` class.
- Added a new `check_auth` function which can be used in resolver methods to check whether the access-token provided in the request authorizes the caller to access resources pertaining to a specific user.
- Added graphene primitive types for the new tables under the `app` schema.
- Added a new `TypeUsers` class with a `by_auth0_id` resource and resolver method to retrieve an application user through their Auth0 ID.
- Added a new `TypeSearches` class with a `by_search_uuid` resource and resolver method to retrieve a user search through its UUID.
- Added a new `utils.py` module with utility functions to clean Auth0 user IDs, retrieve user and search records, as well as functions to delete their dependent records.
- Added new mutation classes `MutationUserUpsert` and `MutationUserDelete` to upsert and delete user records respectively.
- Added new mutation classes `MutationSearchUpsert` and `MutationSearchDelete` to upsert and delete user search records respectively.
- Exposed the new query and mutation resources in the schema.

### v0.3.0

Issue No. 154: Move the age, gender, and year filters from `StudiesListComponent` to `SearchNewComponent`.

- `studies.py`: Updated the `search` and `resolve_search` and added patient-gender and eligibility age-range arguments.

### v0.2.0

Issue No. 154: Move the age, gender, and year filters from `StudiesListComponent` to `SearchNewComponent`.

- `studies_stats.py`: Updated the `get_age_range` attribute and corresponding `resolve_get_age_range` resolver method to make the `study_ids` optional.

### v0.1.2

- Updated the `systemd` service.

### v0.1.0

- Initial release.
