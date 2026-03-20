# the access to operational data needs a setup (based on relevant combinations)
#
# this file defines the setup for the edge cases related to access to operational data
# Access to the cases and case cols depend on the access policies
# they do not depend on the share policies
#
# a case can only be accesssed if
#   there is an organization access policy that grants access to the organization of the user
# AND a user access policy that grants access to the user, both for the case in question
# a case has a case type and a is in a data collection
# it can be in a data collection
# For each case retrieve which data collection it belongs to through the created_in_data_collection_id field and the
# case data collection links table (link table)
#  -> Data collections


# For the edge cases related to access to operational data, we need to set up specific combinations of:
# - organization access policies (org_access)
#    case type (ct) of case is in the case type set of the org access policy yes/no
#    data collection (dc) of case is in the data collection set of the org access policy yes/no
#    column (col) of case is in the column set of the org access policy yes/no
#         for this we will create 2 column sets, one with all columns and one with partial columns
#    so this gives us 8 combinations for org access policies
#    but they can be simplified to 4 combinations by only including the org access policies with the following combinations of case type set, data collection set and column set:
#    dc in set:
#      ct in set:
#        1. col in set (whole colset)
#        2. col not in set (partial colset)
#      3. ct not in set (rest irrelant, because no access to case if ct not in set)
#    4. dc not in set: (rest irrelant, because no access to case if dc not in set)
# - user access policies (user_access)
#    comparable combinations as org access policies
#    dc in set:
#      ct in set:
#        1. col in set (whole colset)
#        2. col not in set (partial colset)
#      3. ct not in set (rest irrelant, because no access to case if ct not in set)
#    4. dc not in set: (rest irrelant, because no access to case if dc not in set)
# we need to combine the 4 org access policy combinations with the 4 user access policy combinations,
# which gives us 16 combinations
# For each of the 16 combinations, we would use the same single case when we
# assume a case belonging to a single data collection
# BUT we want to test a case being in 2 data collections
# and each data collection should have the above 16 combinations of org access and user access policies represented
# and we need 3 data collections and 4 cases for 4 different situations:
# case1 is in dc1
# case2 is in dc2
# case3 is in dc1 and dc2
# case4 is in dc3

# Asssumptions:
# If a case is in 2 data collections and through dc1 it has access to the partial colset
# and through dc2 it has access to the whole colset,
# then the user should have access to the whole colset of the case.
#
# The user only has access to the cases and cols that are in the intersection of the org access policies and user access policies,
# so if either the org access policy or the user access policy does not include the case type, data collection or column,
# then the user should not have access to the case or column.


# We need the following capabilities in the casedb test client:
#
# - Create cases with specific columns
# - Create cases in specific data collections
# - Read cols from the json in the content field of a case

# For testing:
# For each edge case, we need to make assertions for both the cases and the columns in a case
