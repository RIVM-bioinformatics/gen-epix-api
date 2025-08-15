import random
import string
import time
import uuid
from abc import ABC
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Collection, Iterable

import sqlalchemy as sa

from gen_epix.fastapp import BaseRepository, Domain
from gen_epix.omopdb.domain.enum import AnonMethod, AnonStrictness, ServiceType
from gen_epix.omopdb.domain.model.base import Model


class BaseAnonymizer(ABC):
    """
    Functionality that is identical for all Anonymizers, regardless of the type of object they anonymize
    Primarily has datatype / anonymization-method specific functionalities
    Handles anonymization methods & methods: random, categorical, shift
        random: str, int, uuid
        categorical: handles all
        shift: datetime, date

    N.B. method make_null is contemplated but not implemented, if other data types of needed, add them here

    """

    # Some reasonable defaults than can be overidden with keyword arguments
    _MAX_DAYS_OFFSET = 365
    _MIN_DAYS_OFFSET = 1
    _MIN_VALUES_REQUIRED = 10  # for categorical replacements, require a value occurs this many times to be a candidate for use
    _ALLOW_FUTURE_DATES = False

    def __init__(self, seed: int | None = None, **kwargs: Any) -> None:

        self.min_days_offset: int = (
            kwargs.get("min_days_offset") or self._MIN_DAYS_OFFSET
        )
        self.max_days_offset: int = (
            kwargs.get("max_days_offset") or self._MAX_DAYS_OFFSET
        )
        self.min_values_required: int = (
            kwargs.get("min_values_required") or self._MIN_VALUES_REQUIRED
        )
        self.allow_future_dates: bool = (
            kwargs.get("allow_future_dates") or self._ALLOW_FUTURE_DATES
        )

        if not seed:
            seed = int(time.time())
        elif not isinstance(seed, int):
            raise ValueError("Seed must be an integer")
        random.seed(seed)

    def anonymize_dates(self, datelike_values: Collection[date]) -> dict[date, date]:
        """
        Takes a collection of dates and datetimes (may be mixed) and returns a dict that maps these values
        to new date / datetime values. The new dates are such that the new dates preserve the order of dates
        and the time differences in the original such that the new dates preserve the order of dates and the
        time differences in the original collection but has an arbitrary offset from the first date. Offsets
        are integer dates regardless of the data type. No distinction is made between dates and datetimes
        in the treatment, but the output will be of the same type as the input based on python's datetime.datetime
        being a subclass of datetime.date
        """

        datelike_values = list(set(datelike_values))
        offset_days = random.randint(
            self.min_days_offset, self.max_days_offset
        ) * random.choice([-1, 1])
        today = datetime.today().date()
        latest_date = max(
            datelike_values, key=lambda x: x.date() if isinstance(x, datetime) else x
        )
        latest_date = (
            latest_date.date() if isinstance(latest_date, datetime) else latest_date
        )
        latest_date_shifted = latest_date + timedelta(days=offset_days)
        if not self.allow_future_dates and latest_date_shifted > today:
            offset_days = offset_days - (latest_date_shifted - today).days
        offset_days_as_timedelta = timedelta(days=offset_days)
        mapped = {d: d + offset_days_as_timedelta for d in datelike_values}
        return mapped

    def anonymize_text(self, text_values: Collection[str]) -> dict[str, str]:
        text_values = list(set(text_values))
        mapped = dict()
        for tv in text_values:
            len_text = len(tv)
            anon_text = "".join(random.choices(string.ascii_lowercase, k=len_text))
            mapped[tv] = anon_text
        return mapped

    def anonymize_ints(self, int_values: Collection[int]) -> dict[int, int]:
        """
        Take a collection of integers and returns a dict mapping each integer to a new integer
        with the same number of digits and same sign, minimum abs = 1
        """
        int_values = list(set(int_values))
        mapped = dict()
        for i in int_values:
            sign = 1 if i >= 0 else -1
            num_digits = len(str(abs(i)))
            new_int = random.randint(1, 10**num_digits - 1) * sign
            mapped[i] = new_int
        return mapped

    def anonymize_uuids(
        self, uuid_values: Collection[uuid.UUID]
    ) -> dict[uuid.UUID, uuid.UUID]:
        """
        Take a collection of uuid.UUID objects and returns a dict mapping each uuid.UUID to a new uuid.UUID
        N.B. iLES has no uuids that need to be anonymized, so this has not been tested
        """
        uuid_values = list(set(uuid_values))
        mapped = {u: uuid.uuid4() for u in uuid_values}
        return mapped

    def anonymize_categorical(
        self, categorical_values: Iterable[Any], choices: Collection[Any]
    ) -> dict[Any, Any]:
        """
        Take a collection of categorical values and returns a dict mapping each value to a new value
        among the choices provided. Excludes None and "" from the choices, as that may cause conflicts even
        if it's allowable in the data or just be confusing to the user.

        TODO (possible): implement proportional choices, i.e., make assignment more likely depending how
        often a value occurs in the input choices collection.

        @Ivo: By choice I've made this accept any Collection for choices, not just a set. Forcing it to
        accept a set requires the coder to take that step prior to calling, which I don't see
        the point of doing. The return is a dict, so duplicates are eliminated in this step, why
        do it elsewhere? Further, if we implement proportional choices, another the reason NOT
        to require a set as input, b/c then we'd just have to count frequency outside this method
        which is likely not relevant outside this method

        :param categorical_values: the values to be anonymized
        :param choices: the possible replacement values
        :return: a dict mapping the original values to the new values
        """
        choices = list(set(choices))
        excluded = [None, ""]
        choices = [c for c in choices if c not in excluded]
        mapped = {v: random.choice(choices) for v in categorical_values}
        return mapped


class ModelAnonymizer(BaseAnonymizer):
    """
    ModelAnonymizer handles a instances of "subject" models that are are built from models in the Domain specified.
    For instance, IlesSubject is built from the models in the Iles domain.
    A "subject" model has fields that are data values, or lists of other models. Such submodels can only contain data values
    in their fields.
    """

    def __init__(
        self,
        domain: Domain,
        repository: BaseRepository,
        seed: int | None = None,
        strictness_level: AnonStrictness = AnonStrictness.STRICT,
        **kwargs: Any,
    ) -> None:
        super().__init__(seed, **kwargs)

        self.domain = domain
        self.repository = repository
        self.strictness_level = strictness_level

        self.categorical_loc_values = self.identify_and_load_categoricals()

    def attach_model_instance(self, model: Model) -> None:
        self.model = model

    def identify_and_load_categoricals(self):
        """
        Inspect the models that are present in the domain and figure out which model/fields are specified
        as anonymization_method=AnonMethod.CATEGORICAL. For these, load all the data
        available (or NYI: possibly reduced scope) as possible substitutable values
        """
        model_classes = self.domain.get_dag_sorted_models(service_type=ServiceType.OMOP)
        categorical_locs = []
        for model_class in model_classes:
            for field_name, field in model_class.model_fields.items():
                if jse := getattr(field, "json_schema_extra", None):
                    if jse.get("anonymization_method") == AnonMethod.CATEGORICAL.value:
                        categorical_locs.append((model_class, field_name))
        # TODO: rework categorical_locs into a dict so we can group by model_class, so we only have to read each model once
        categorical_loc_values = defaultdict(lambda: defaultdict(set))
        for model_class, field_name in categorical_locs:
            mapper = self.repository.get_mapper(model_class)
            sa_model_class = (
                mapper.row_class
            )  # why is this called row_class? it's the SA model class!
            with self.repository.uow() as uow:
                # @Ivo: What there a better way through the interface you built to access a single column?
                results = uow.session.execute(
                    sa.select(sa_model_class.__table__.c[field_name])
                )
                values = [t[0] for t in results.fetchall()]
                value_counts = Counter(values)
                values_culled = set(
                    [
                        val
                        for val, ct in value_counts.items()
                        if ct >= self._MIN_VALUES_REQUIRED
                    ]
                )
                categorical_loc_values[model_class][field_name] = values_culled
        return categorical_loc_values

    def create_anonymization_map(
        self, model: Model
    ) -> dict[tuple[type, AnonMethod], list[tuple[tuple[Any], Any]]]:
        """
        Builds a map to the data to be anonymized by reading the models in the domain, which
        themselves contain an indication of whether and how each field needs to be treated.

        Output is a dict of lists:
            { (type, anon_method): [((field_name,), value), ((field_name, i), value), ...] }
            where:
                key: tuple with the datatype and method of anonymization
                value: lists of tuples, where each tuple contains a path to the field and the field value

        The first tuple in the dict value is the path to the field in the model, which can be a
        1-tuple, 2-tuple, or 3-tuple. See discussion in get_nested_attribute() regarding the limitation of
        the structures in self.model that can be handled.

        :param model: the (pydantic) model to be scanned
        """

        anon_map = defaultdict(list)
        for field_name, field in model.model_fields.items():
            value = getattr(model, field_name, None)
            type_ = type(value)
            if value is None:
                # Don't need to do anything if there's no data
                continue
            if isinstance(value, list):
                # Always work through elements of lists
                to_anonymize = True
            else:
                to_anonymize = field.json_schema_extra.get("to_anonymize", None)
                if to_anonymize:
                    anon_method = AnonMethod(
                        field.json_schema_extra.get("anonymization_method", None)
                    )
            if (value is not None or value == "") and to_anonymize is None:
                msg = (
                    f"Must declare anonymization intent for every field with data. Found "
                    f"data in {model.__class__.__name__}.{field_name} (={value}) but no anonymization intent."
                )
                if self.strictness_level == AnonStrictness.IGNORE:
                    pass
                elif self.strictness_level == AnonStrictness.WARN:
                    print("WARNING: ", msg)
                elif self.strictness_level == AnonStrictness.STRICT:
                    raise ValueError(msg)
                else:
                    raise ValueError(
                        f"No logic for strictness_level = {self.strictness_level}"
                    )
            if not to_anonymize:
                continue
            if type_ not in (Model, list):
                anon_map[type_, anon_method].append(((field_name,), value))
            elif isinstance(value, Model):
                sub_locs = self.create_anonymization_map(value)
                for typ_meth_tup, loc_value_tups in sub_locs.items():
                    anon_map[typ_meth_tup].extend(
                        [((field_name,) + k, v) for k, v in loc_value_tups]
                    )
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    if isinstance(v, Model):
                        sub_locs = self.create_anonymization_map(v)
                        for typ_meth_tup, loc_value_tups in sub_locs.items():
                            anon_map[typ_meth_tup].extend(
                                [((field_name, i) + k, v) for k, v in loc_value_tups]
                            )
                    else:
                        anon_map[type_, anon_method].append(((field_name, i), v))
        return anon_map

    def anonymize(self) -> Model:
        """
        Anonymizes the model according to the specification and returns the anonymized model
        At present anonymization_spec is not handled as we haven't yet designed it.
        """

        def validate_location_path(path: tuple[str | int, ...]) -> bool:
            """
            Validate the path to ensure it is matches expected form (see get_nested_attribute)
            """
            if not isinstance(path, tuple):
                raise ValueError(f"Invalid path: {path}. Path must be a tuple")
            elif len(path) == 1 and isinstance(path[0], str):
                return True
            elif (
                len(path) == 2 and isinstance(path[0], str) and isinstance(path[1], str)
            ):
                return True
            elif (
                len(path) == 2 and isinstance(path[0], str) and isinstance(path[1], int)
            ):
                return True
            elif (
                len(path) == 3
                and isinstance(path[0], str)
                and isinstance(path[1], int)
                and isinstance(path[2], str)
            ):
                return True
            else:
                raise ValueError(
                    f"Invalid path: {path}. Path must be a 1-tuple, 2-tuple, or 3-tuple of strings and/or integers"
                )

        def get_nested_attribute(model: Model, path: tuple[str | int, ...]) -> Any:
            """
            Get the value of a nested attribute in a model using a tuple path
            that indicates where in the model the attribute is located.
            :param path: Either a 1-tuple, 2-tuple, or 3-tuple like:
                ("field_name",): specifies a scalar field at top-level
                ("field_name", "subfield_name"): specifies a scalar field within a field that is itself a model
                ("field_name", 1, "subfield_name:): specifies a scalar fields within a model that is the first instance in a list of models
                N.B. This does not handle nested models that contain lists themselves
            """
            validate_location_path(path)
            current = model
            for key in path:
                if isinstance(key, int):
                    current = current[key]
                else:
                    current = getattr(current, key)
            return current

        def get_nested_attribute_model_field_name(
            model: Model, path: tuple[str | int, ...]
        ) -> tuple[Model, str]:
            """
            Get the model and field name corresponding to the end of a path in the nested structure
            See explanation of 'path' in sister method get_nested_attribute
            """
            validate_location_path(path)
            current = model
            for i, key in enumerate(path):
                if isinstance(key, int):
                    current = current[key]
                else:
                    # If this is the last step in the path, return (model, field name)
                    if i == len(path) - 1:
                        return current, key
                    current = getattr(current, key)
            raise ValueError("Invalid path: must end in a field access.")

        def set_nested_attribute(
            model: Model, path: tuple[str | int, ...], value: Any
        ) -> None:
            """See explanation of 'path' in sister method get_nested_attribute"""
            validate_location_path(path)
            current = model
            for key in path[:-1]:
                if isinstance(key, int):
                    current = current[key]
                else:
                    current = getattr(current, key)
            setattr(current, path[-1], value)

        def map_nested_attributes(
            model: Model, path: tuple[str], mapping: dict[Any, Any]
        ) -> None:
            """See explanation of 'path' in sister method get_nested_attribute"""
            curr_value = get_nested_attribute(model, path)
            mapped_value = mapping.get(curr_value, curr_value)
            set_nested_attribute(model, path, mapped_value)

        if not hasattr(self, "model") or not isinstance(self.model, Model):
            raise ValueError("No model attached to anonymizer!")
        anonymization_map = self.create_anonymization_map(self.model)

        # Now that we've collected all the data that needs to be anonymized, let's do it!
        # Handle data types/methods each in their own way

        collected_payloads = []

        # ints/random
        # collected_ints, anonymized_int_map = {}, {}
        if loc_value_tups := anonymization_map.pop((int, AnonMethod.RANDOM), None):
            collected_ints = dict(loc_value_tups)
            anonymized_int_map = self.anonymize_ints(collected_ints.values())
            collected_payloads.append((collected_ints, anonymized_int_map))

        # strings/random
        # collected_strings, anonymized_string_map = {}, {}
        if loc_value_tups := anonymization_map.pop((str, AnonMethod.RANDOM), None):
            collected_strings = dict(loc_value_tups)
            anonymized_string_map = self.anonymize_text(collected_strings.values())
            collected_payloads.append((collected_strings, anonymized_string_map))

        # dates/shift - captures both dates and datetimes (latter subclass of former) [CHECK IF works with .pop here]
        # collected_dates, anonymized_date_map = {}, {}
        if loc_value_tups := anonymization_map.pop((datetime, AnonMethod.SHIFT), None):
            collected_dates = dict(loc_value_tups)
            anonymized_date_map = self.anonymize_dates(collected_dates.values())
            collected_payloads.append((collected_dates, anonymized_date_map))

        # categoricals
        # for these we need to reference a lookup dict of possible values distinct for each model/field
        # and make each location a separate payload item
        categorical_loc_value_tups = []
        keys = list(anonymization_map)
        for key in keys:
            if key[1] == AnonMethod.CATEGORICAL:
                categorical_loc_value_tups.extend(anonymization_map.pop(key))
        categorical_payload_items = []
        for tup in categorical_loc_value_tups:
            path, value = tup
            model_inst, field_name = get_nested_attribute_model_field_name(
                self.model, path
            )
            model_class = model_inst.__class__
            choices = self.categorical_loc_values.get(model_class, {}).get(
                field_name, None
            )
            if not choices:
                raise ValueError(
                    f"Categorical anonymization requested for {model_class}.{field_name} but no choices were found"
                )
            else:
                # Even though it's a little hokey, build the payload item to match the others
                # so we can use map_nested_attributes to process them. Hokey here means the
                # map_ is a 1:1 dict.
                # TODO: replace with general method tof choosing replacement value that could be enhanced, e.g.,
                # with a relative frequency, or excluding certain possibilities
                # map_ = {value:  random.choice(list(choices))}
                map_ = self.anonymize_categorical([value], choices)
                categorical_payload_items.append(({path: None}, map_))
        collected_payloads.extend(categorical_payload_items)

        # Check we've set up processing for all data
        if anonymization_map:
            msg = f"Could not find anomyization methods requested: {anonymization_map.keys()}"
            if self.strictness_level == AnonStrictness.IGNORE:
                pass
            elif self.strictness_level == AnonStrictness.WARN:
                print("WARNING: ", msg)
            elif self.strictness_level == AnonStrictness.STRICT:
                raise ValueError(msg)
            else:
                raise ValueError(
                    "AnonStrictness level not recognized: {self.strictness_level}"
                )
        # else:
        #    print("Found methods for all anonymization methods requested")

        # Final step: Make the substitutions in the top-level model
        anonymized_model = self.model.model_copy(deep=True)
        for location_dict, map_ in collected_payloads:
            for location in location_dict:
                map_nested_attributes(anonymized_model, location, map_)

        # Altering the model with map_nested_attributes results in dicts inside - need to convert back into model
        anonymized_model = type(anonymized_model).model_validate(
            anonymized_model.model_dump(), strict=True
        )

        self.anonymized_model = anonymized_model

        return anonymized_model

    # @John: can you move this to the unit test for the ModelAnonymizer class?
    # @Ivo: This does not fit in the unit test framework. This is meant for human inspection
    # of the anonymization to see if it's working. There's probably a better place for it
    # than here, but that can be dealt with later. Additionally, yes, unit tests could/should
    # be developed.
    def compare_models(self, fp_to_output: Path | None = None) -> None:
        """
        Prints or writes to file formatted comparison of original and anonymized models,
        for development and testing purposes.
        """
        _KEY_PAD = 60
        _VALUE_PAD = 25
        orig_model = self.model.model_dump()
        anon_model = self.anonymized_model.model_dump()
        assert orig_model.keys() == anon_model.keys()
        out_str = ""

        def assert_same_structure(a, b, path="") -> str:
            if type(a) != type(b):
                raise ValueError(
                    f"Type mismatch at {path or '<root>'}: {type(a)} vs {type(b)}"
                )

            if isinstance(a, dict):
                if a.keys() != b.keys():
                    raise ValueError(
                        f"Dict key mismatch at {path or '<root>'}: {set(a.keys())} vs {set(b.keys())}"
                    )
                for k in a:
                    assert_same_structure(a[k], b[k], f"{path}.{k}" if path else k)

            elif isinstance(a, list):
                if len(a) != len(b):
                    raise ValueError(
                        f"List length mismatch at {path or '<root>'}: {len(a)} vs {len(b)}"
                    )
                for i, (item_a, item_b) in enumerate(zip(a, b)):
                    assert_same_structure(item_a, item_b, f"{path}[{i}]")

        def comp_struct(a, b, out_str, path=""):
            if isinstance(a, dict):
                for k in a:
                    new_path = f"{path}.{k}" if path else k
                    out_str = comp_struct(a[k], b[k], out_str, new_path)

            elif isinstance(a, list):
                for i, (item_a, item_b) in enumerate(zip(a, b)):
                    new_path = f"{path}[{i}]"
                    out_str = comp_struct(item_a, item_b, out_str, new_path)

            else:
                fmt_comp = f"{path[:_KEY_PAD]:<{_KEY_PAD}} | diff = {str(a != b):<6} | {str(a)[:_VALUE_PAD]:<{_VALUE_PAD}} | {str(b)[:_VALUE_PAD]}\n"
                out_str += fmt_comp

            return out_str

        assert_same_structure(orig_model, anon_model)
        out_str = comp_struct(orig_model, anon_model, out_str)

        if fp_to_output:
            with open(fp_to_output, "w") as f:
                f.write(out_str)
        else:
            print(out_str)
