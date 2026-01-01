"""
Unit tests for commondb upload services.

The tests make use of the Parent, Child1, and Child2 and derived models defined in
model.py and focus on verifying the upload logic.

The tests handle all of the following scenarios, as well as any relevant combinations thereof:
1 Existence of parent and/or child objects in the repository
1.1 ID not provided or NULL_ID: object does not exist and needs to be created
1.2 ID provided and is_new_id=True
1.2.1 Object with this ID does not exist: error
1.2.2 Object with this ID exists: needs to be created with that ID
2 Provision of child objects (all need to be created/updated)
2.1 Parent without any Child1 or Child2 objects
2.2 Parent with Child1 objects only
2.3 Parent with Child2 objects only
2.4 Parent with both Child1 and Child2 objects
3 Links to reference data in child objects
3.1 Child object with reference data model ID (any except NULL_ID) and no code
3.1.1 Reference model ID not found: error
3.1.1 Reference model ID found: no issue
3.2 Child object with reference data model code and no ID (or NULL_ID)
3.2.1 Reference model code not found: error
3.2.2 Reference model code found: set reference model ID in Child object
3.3 Child object with both reference model ID (any except NULL_ID) and reference model code
3.3.1 Reference model ID and code do not match: error
3.3.2 Reference model ID and code match: no issue
3.4 Child2 object with no ID (or NULL_ID) and no code (reference is optional for Child2)
3.4.1 NULL_ID provided: set to None
3.4.2 NULL_ID not provided: no issue
4 Parent link in child objects
4.1 NULL_ID: not provided, parent object's ID (after creation, if applicable) to be set during upload
4.2 Actual parent ID
4.2.1 Parent does not exist yet or has different ID: error
4.2.2 Parent exists with that ID: no issue
5 Field mutability for parent and child objects that are already stored and will therefore be updated
5.1: Field that is always mutable
5.1.1: Single value field: field is set to new value
5.1.2: List field: field is set to new list of values
5.1.3: Dict field: individual keys in dict are updated/added/removed:
5.1.3.1 New key, new value not None: add key/value
5.1.3.2 New key, new value is None: do not add key
5.1.3.3 Existing key, new value not None: update key to new value
5.1.3.4 Existing key, new value is None: remove key
5.2: Field that is mutable if empty
5.2.1: Stored value is empty (None, empty list, empty dict): field is set to new value
5.2.2: Stored value is not empty, new value is empty: no issue
5.2.3: Stored value is not empty, new value is not empty: error
6 Provision of external identifiers for parent objects (use IdentifierType=PERSON for testing purposes)
6.1 No external identifiers provided: no issue
6.2 One external identifier provided
6.2.1 Existing external identifier i.e. (identifier_issuer, external_id) combination exists already
6.2.1.1 Parent ID None or NULL_ID: set parent ID in upload result
6.2.1.2 Parent ID provided
6.2.1.2.1 Same as existing external identifiers' parent ID: no issue
6.2.1.2.2 Different from existing external identifiers' parent ID: error
6.2.2 New external identifier i.e. (identifier_issuer, external_id) combination does not exist yet for this parent: create new external identifier once parent ID is known
6.2.3 Multiple external identifiers provided
6.2.3.1 Some existing external identifiers: must all point to the same parent ID AND same restrictions as 6.2 per external identifier
6.2.3.2 All new external identifiers: create new external identifiers once parent ID is known
7 Upload command on_exists value
7.1 ERROR: error if any existing object
7.2 SKIP: skip any existing object, do not update
7.3 UPDATE: update any existing object
"""
