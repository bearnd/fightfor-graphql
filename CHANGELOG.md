## Changelog

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
