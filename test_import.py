from gen_epix.commondb.domain.util import set_env_variables

# from gen_epix.commondb.domain import model as model

# Force the util module to load first by importing it directly,
# bypassing the circular import triggered via domain.__init__
print("Attempting import: from gen_epix.commondb.util import set_env_variables")


print("Import successful!")
print(f"set_env_variables: {set_env_variables}")
print(f"Signature requires: app_type, dev_idp_config, dev_repository_config")
