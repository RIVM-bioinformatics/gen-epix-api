# TODO: resolve import now that omop is a separate package
# # N.B. This test is only here for a proof of concept.
# # It needs to be integrated into the full test suite, including moved to the correct location.
# import inspect
# from pathlib import Path

# from omop.omop.generation_utils import BioBasePydanticModelGenerator
# from pydantic import BaseModel

# from gen_epix.omopdb.domain.model import omop


# def get_static_models(module):
#     # Retrieve all classes defined in a module that inherit from BaseModel
#     return [
#         obj
#         for name, obj in inspect.getmembers(module)
#         if inspect.isclass(obj)
#         and issubclass(obj, BaseModel)
#         and obj is not BaseModel  # Exclude BaseModel itself
#     ]


# # def remove_keys(schema, keys_to_remove):
# #    """
# #    Recursively remove all occurrences of the specified keys from the schema.
# #
# #
# #    :param schema: The JSON schema dictionary.
# #    :param keys_to_remove: A set or list of keys to remove.
# #    """
# #    if isinstance(schema, dict):
# #        # Remove any keys we want to filter out at this level.
# #        for key in keys_to_remove:
# #            schema.pop(key, None)
# #        # Process nested dictionaries or lists.
# #        for value in schema.values():
# #            remove_keys(value, keys_to_remove)
# #    elif isinstance(schema, list):
# #        for item in schema:
# #            remove_keys(item, keys_to_remove)
# #    return schema


# def test_compare_omop_model_defs_with_spec():
#     # Generate models from the specs
#     # Note path to spec_dir depends on how omop is imported
#     spec_dir = (
#         Path(__file__).parent.parent.parent.parent.parent
#         / "omopdb"
#         / "data"
#         / "extract"
#         / "omop_spec"
#     )
#     custom_template_dir = spec_dir / "custom_templates"
#     mg = BioBasePydanticModelGenerator(spec_dir)
#     freshly_generated_models = mg.generate_dynamic_models()

#     # Get the static models (in code)
#     static_models = get_static_models(omop)
#     # Manually remove items that are in the static definitions that we don't expect to have in the
#     # dynamically generated models (i.e., those that are imported)
#     static_models = [
#         model
#         for model in static_models
#         if model.__name__ not in ["Model", "User", "Entity", "RootModel"]
#     ]

#     # Compare the generated models to the static models

#     # The first thing is that we have the same field names!
#     freshly_generated_model_names = {
#         model.__name__ for model in freshly_generated_models
#     }
#     static_model_names = {model.__name__ for model in static_models}
#     assert freshly_generated_model_names == static_model_names

#     # Now compare the field themselves
#     model_tuples = {}
#     for name in freshly_generated_model_names:
#         model_tuples[name] = (
#             next(model for model in freshly_generated_models if model.__name__ == name),
#             next(model for model in static_models if model.__name__ == name),
#         )
#     # We add certain items when defining the models for dynamic generation that are passed through
#     # to the JSON schema, and which have influence on the specification of the model definitions in the
#     # code, but which are not actually part of the model definitions themselves. We need to remove these.
#     keys_to_remove = {"annotation", "title", "json_schema_extra", "$comment", "is_pk"}
#     # gen_epix.omopdb.domain.model.base.Model is the parent class of all models, and it has an 'id' field
#     # but this is not present in the spec, rather in the build of the models in the code
#     # so we have to ignore it
#     fields_to_ignore = {"id"}
#     for tup in model_tuples.values():
#         fields0 = frozenset([k for k in tup[0].__fields__.keys()])
#         fields1 = frozenset(
#             [k for k in tup[1].__fields__.keys() if k not in fields_to_ignore]
#         )
#         assert fields0 == fields1
#         for f in fields0:
#             attr0 = {
#                 k: v
#                 for k, v in inspect.getmembers(tup[0].__fields__[f])
#                 if not callable(v) and not k.startswith("_") and k not in keys_to_remove
#             }
#             attr1 = {
#                 k: v
#                 for k, v in inspect.getmembers(tup[1].__fields__[f])
#                 if not callable(v) and not k.startswith("_")
#                 if not callable(v) and not k.startswith("_") and k not in keys_to_remove
#             }
#             # if 'title' in attr0:
#             #    attr0.pop('title')
#             # if 'title' in attr1:
#             #    attr1.pop('title')
#             assert attr0 == attr1
