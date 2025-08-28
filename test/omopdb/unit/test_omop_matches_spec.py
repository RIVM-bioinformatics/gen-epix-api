import re
from pathlib import Path
from typing import Any, Type

import pandas as pd

from gen_epix.omopdb.domain import model
from gen_epix.omopdb.domain.model.base import Model
from gen_epix.omopdb.domain.model.omop.base import DataLineageMixin

TABLE_METADATA_FILE = (
    Path(__file__).parent.parent.parent.parent
    / "data"
    / "omopdb"
    / "specification"
    / "OMOP_CDMv6.0_Table_Level.csv"
)

FIELD_METADATA_FILE = (
    Path(__file__).parent.parent.parent.parent
    / "data"
    / "omopdb"
    / "specification"
    / "OMOP_CDMv6.0_Field_Level.csv"
)

MODEL_BY_TABLE: dict[str, Type[model.Model]] = {
    # Ordered topologically based on foreign key dependencies
    # Foundation tables (no dependencies)
    "location": model.Location,
    "cohort_definition": model.CohortDefinition,
    "cohort": model.Cohort,
    "cdm_source": model.CdmSource,
    # Vocabulary system (circular dependencies resolved logically)
    "vocabulary": model.Vocabulary,
    "domain": model.Domain,
    "concept_class": model.ConceptClass,
    "concept": model.Concept,
    "relationship": model.Relationship,
    # Concept relationships (depend on concept and relationship)
    "concept_relationship": model.ConceptRelationship,
    "concept_ancestor": model.ConceptAncestor,
    "concept_synonym": model.ConceptSynonym,
    # Reference/mapping tables
    "drug_strength": model.DrugStrength,
    "source_to_concept_map": model.SourceToConceptMap,
    "metadata": model.Metadata,
    # Care infrastructure
    "care_site": model.CareSite,
    "provider": model.Provider,
    # Person and observations
    "person": model.Person,
    "observation_period": model.ObservationPeriod,
    "payer_plan_period": model.PayerPlanPeriod,
    # Visits (depend on person, care_site, provider, concept)
    "visit_occurrence": model.VisitOccurrence,
    "visit_detail": model.VisitDetail,
    # Clinical events (depend on person, visits, providers, concepts)
    "condition_occurrence": model.ConditionOccurrence,
    "procedure_occurrence": model.ProcedureOccurrence,
    "drug_exposure": model.DrugExposure,
    "device_exposure": model.DeviceExposure,
    "measurement": model.Measurement,
    "observation": model.Observation,
    "specimen": model.Specimen,
    "note": model.Note,
    # Other tables depending at least on person
    "condition_era": model.ConditionEra,
    "drug_era": model.DrugEra,
    "dose_era": model.DoseEra,
    "note_nlp": model.NoteNlp,
    "cost": model.Cost,
    "location_history": model.LocationHistory,
    "survey_conduct": model.SurveyConduct,
    # General relationships
    "fact_relationship": model.FactRelationship,
    "measurement_relation": model.MeasurementRelation,
}

DATA_LINEAGE_TABLES = {
    # Person and observations
    "person",
    "observation_period",
    "payer_plan_period",
    # Visits (depend on person, care_site, provider, concept)
    "visit_occurrence",
    "visit_detail",
    # Clinical events (depend on person, visits, providers, concepts)
    "condition_occurrence",
    "procedure_occurrence",
    "drug_exposure",
    "device_exposure",
    "measurement",
    "observation",
    "specimen",
    "note",
    # Other tables depending at least on person
    "condition_era",
    "drug_era",
    "dose_era",
    "note_nlp",
    "cost",
    "location_history",
    "survey_conduct",
}

OMOP_DATATYPE_STR_MAP = {
    "bigint": ("int", ""),
    "date": ("date", ""),
    "datetime": ("datetime", ""),
    "float": ("float", ""),
    "integer": ("int", ""),
    "varchar(1)": ("str", ", max_length=1"),
    "varchar(2)": ("str", ", max_length=2"),
    "varchar(9)": ("str", ", max_length=9"),
    "varchar(10)": ("str", ", max_length=10"),
    "varchar(20)": ("str", ", max_length=20"),
    "varchar(25)": ("str", ", max_length=25"),
    "varchar(50)": ("str", ", max_length=50"),
    "varchar(55)": ("str", ", max_length=55"),
    "varchar(60)": ("str", ", max_length=60"),
    "varchar(100)": ("str", ", max_length=100"),
    "varchar(250)": ("str", ", max_length=250"),
    "varchar(255)": ("str", ", max_length=255"),
    "varchar(1000)": ("str", ", max_length=1000"),
    "varchar(2000)": ("str", ", max_length=2000"),
    "varchar(max)": ("str", ""),
}

OMOP_MODULE_HEADER = """
from datetime import date, datetime
from typing import ClassVar
from uuid import UUID
from pydantic import Field

from gen_epix.common.domain.model import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.omopdb.domain.model.omop.base import DataLineageMixin
"""

SA_OMOP_MODULE_HEADER = """
from datetime import date, datetime
from typing import Type
from uuid import UUID

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped

from gen_epix.common.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)
from gen_epix.omopdb.domain import DOMAIN, enum, model
from gen_epix.omopdb.repositories.sa_model.base import DataLineageMixin

Base: Type = orm.declarative_base(name=enum.ServiceType.OMOP.value)
"""


class TestOmopSpecification:

    def test_model_specification(self) -> None:
        def _is_yes(x: Any) -> bool:
            return x.upper() == "YES" if isinstance(x, str) else False

        def _get_sort_index(x: Any) -> int:
            return (
                sort_index_map.get(x.lower(), len(sort_index_map))
                if isinstance(x, str)
                else 0
            )

        def _get_repr(x: Any) -> str:
            return (
                x.__repr__()[1:-1].replace(r'"', r"\"")
                if isinstance(x, str)
                else x.__repr__()
            )

        # Parse specification and sort tables topologically
        table_df = pd.read_csv(TABLE_METADATA_FILE)
        field_df = pd.read_csv(FIELD_METADATA_FILE)
        sort_index_map = {x: i for i, x in enumerate(MODEL_BY_TABLE)}
        table_df["sort_index"] = table_df["cdmTableName"].map(_get_sort_index)
        table_df.sort_values(by="sort_index", inplace=True)
        field_df["is_primary_key"] = field_df["isPrimaryKey"].apply(_is_yes)
        field_df["is_foreign_key"] = field_df["isForeignKey"].apply(_is_yes)
        field_df["table_sort_index"] = field_df["cdmTableName"].map(_get_sort_index)
        field_df["foreign_key_table_sort_index"] = field_df["fkTableName"].map(
            _get_sort_index
        )
        field_df["is_acyclic_foreign_key"] = (
            field_df["foreign_key_table_sort_index"] < field_df["table_sort_index"]
        )

        # Verify specification
        mask = field_df["is_foreign_key"] != field_df["fkFieldName"].notna()
        if mask.any():
            foreign_key_str = ", ".join(
                f"({x},{y})"
                for x, y in zip(
                    field_df.loc[mask, "cdmTableName"],
                    field_df.loc[mask, "cdmFieldName"],
                )
            )
            raise ValueError(
                f"Foreign key and foreign key table inconsistent: {foreign_key_str}"
            )

        error_messages = []
        all_code_lines = []
        all_sa_code_lines = []
        for _, table_row in table_df.iterrows():
            code_lines = []
            sa_code_lines = []
            table_name = table_row["cdmTableName"].lower()
            field_mask = field_df["cdmTableName"] == table_name
            primary_key_mask = field_mask & (
                field_df["isPrimaryKey"].str.upper() == "YES"
            )
            foreign_key_mask = (
                field_mask
                & (field_df["isForeignKey"].str.upper() == "YES")
                & field_df["is_acyclic_foreign_key"]
            )
            if primary_key_mask.sum() > 1:
                raise ValueError(
                    f"Table {table_name} has multiple primary keys defined."
                )
            elif not primary_key_mask.any():
                raise ValueError(f"Table {table_name} has no primary key defined.")
            # Check table metadata
            if table_name.lower() not in MODEL_BY_TABLE:
                error_messages.append(f"No model defined for table: {table_name}")
                continue
            model_class = MODEL_BY_TABLE[table_name.lower()]
            entity = model_class.ENTITY
            assert entity is not None
            table_expected_description = table_row["tableDescription"]
            table_actual_description = model_class.__doc__
            if re.sub(r"\s+", "", table_expected_description) != re.sub(
                r"\s+", "", table_actual_description
            ):
                error_messages.append(
                    f"Table description for {table_name} not found in model docstring:"
                )
                error_messages.append(
                    f"\tExpected docstring:\n{table_expected_description}"
                )
                error_messages.append(
                    f"\tActual docstring:\n{table_actual_description}"
                )

            # Add to class level generated code lines
            if table_name in DATA_LINEAGE_TABLES:
                code_lines.append(
                    f"class {model_class.__name__}(Model, DataLineageMixin):"
                )
            else:
                code_lines.append(f"class {model_class.__name__}(Model):")
            code_lines.append(f'\t"""{table_expected_description}"""')
            primary_key_field_names = field_df.loc[
                primary_key_mask, "cdmFieldName"
            ].tolist()
            if primary_key_field_names:
                # keys_str = (
                #     ", keys=create_keys({"
                #     + ", ".join(
                #         f'{i+1}: "{x}"' for i, x in enumerate(primary_key_field_names)
                #     )
                #     + "})"
                # )
                id_field_name_str = f', id_field_name="{primary_key_field_names[0]}"'
            else:
                # keys_str = ""
                id_field_name_str
            foreign_key_from_field_names = field_df.loc[
                foreign_key_mask, "cdmFieldName"
            ].tolist()
            foreign_key_to_table_names = (
                field_df.loc[foreign_key_mask, "fkTableName"].str.lower().tolist()
            )
            foreign_key_to_model_classes = [
                MODEL_BY_TABLE[x] for x in foreign_key_to_table_names
            ]
            if foreign_key_from_field_names:
                foreign_keys_str = (
                    ", links=create_links({"
                    + ", ".join(
                        f'{i+1}: ("{x[0]}", {x[1].__name__}, None)'
                        for i, x in enumerate(
                            zip(
                                foreign_key_from_field_names,
                                foreign_key_to_model_classes,
                            )
                        )
                    )
                    + "})"
                )
            else:
                foreign_keys_str = ""
            code_lines.append(
                f'\tENTITY: ClassVar = Entity(snake_case_plural_name="{entity.snake_case_plural_name}", table_name="{entity.table_name}", persistable={entity.persistable}{id_field_name_str}{foreign_keys_str})'
            )
            if table_name in DATA_LINEAGE_TABLES:
                sa_code_lines.append(
                    f"class {model_class.__name__}(Base, DataLineageMixin, RowMetadataMixin):"
                )
            else:
                sa_code_lines.append(
                    f"class {model_class.__name__}(Base, RowMetadataMixin):"
                )
            sa_code_lines.append(
                f"    __tablename__, __table_args__ = create_table_args(model.{model_class.__name__})"
            )
            sa_code_lines.append("")

            # Check field metadata
            extra_fields = {x: y for x, y in model_class.model_fields.items()}
            for _, field_row in field_df[field_mask].iterrows():
                field_name: str = field_row["cdmFieldName"]
                extra_fields.pop(field_name, None)
                is_required = field_row["isRequired"].upper() == "YES"
                datatype = OMOP_DATATYPE_STR_MAP[field_row["cdmDatatype"].lower()]
                is_primary_key = field_row["is_primary_key"]
                is_foreign_key = field_row["is_foreign_key"]
                if is_primary_key or is_foreign_key or field_name.endswith("_id"):
                    # Change datatype of primary and foreign keys to UUID
                    if datatype[0] not in {"int", "str"}:
                        error_messages.append(
                            f"Primary or foreign key field {field_name} in table {table_name} is not of type int: {datatype[0]}."
                        )
                    else:
                        datatype = ("UUID", "")

                # Add to field level generated code lines
                annotation = datatype[0] + ("" if is_required else " | None")
                default = "" if is_required else "default=None, "
                user_guidance = field_row["userGuidance"]
                has_user_guidance = (
                    isinstance(user_guidance, str) and user_guidance.strip() != ""
                )
                etl_conventions = field_row["etlConventions"]
                has_etl_conventions = (
                    isinstance(etl_conventions, str) and etl_conventions.strip() != ""
                )
                description = (
                    '"'
                    + r"User guidance:\n"
                    + (_get_repr(user_guidance) if has_user_guidance else "None")
                    + r"\nETL conventions:\n"
                    + (_get_repr(etl_conventions) if has_etl_conventions else "None")
                    + '"'
                )
                code_lines.append(
                    f"\t{field_name}: {annotation} = Field({default}description={description}{datatype[1]})"
                )
                sa_code_lines.append(
                    f'    {field_name}: Mapped[{annotation}] = create_mapped_column(DOMAIN, model.{model_class.__name__}, "{field_name}")'
                )

                # Check metadata
                if field_name not in model_class.model_fields:
                    error_messages.append(
                        f"Field {field_name} not found in model {model_class.__name__}."
                    )
                    continue
                field_info = model_class.model_fields[field_name]
                field_expected_description = description[1:-1]
                field_actual_description = _get_repr(field_info.description)
                if field_expected_description != field_actual_description:
                    error_messages.append(
                        f"Field description for {field_name} not found in model {model_class.__name__}."
                    )
                    error_messages.append(
                        f"\tExpected description:\n{field_expected_description}"
                    )
                    error_messages.append(
                        f"\tActual description:\n{field_actual_description}"
                    )

            for field_name in DataLineageMixin.__dict__:
                extra_fields.pop(field_name, None)
            for field_name in Model.model_fields:
                extra_fields.pop(field_name, None)
            for field_name, field_info in extra_fields.items():
                code_lines.append(
                    f'\t{field_name}: str | None = Field(default=None, description="TO_ADJUST")'
                )
            all_code_lines.extend(code_lines)
            all_sa_code_lines.extend(sa_code_lines)

            # Write single model to file
            output_file = (
                Path(__file__).parent.parent.parent / "output" / f"{table_name}.py"
            )
            with open(output_file, "w") as f:
                f.write("\n".join([OMOP_MODULE_HEADER, *code_lines]))
            sa_output_file = (
                Path(__file__).parent.parent.parent / "output" / f"{table_name}.sa.py"
            )
            with open(sa_output_file, "w") as f:
                f.write("\n".join([SA_OMOP_MODULE_HEADER, *sa_code_lines]))

        # Write all models to single file
        output_file = (
            Path(__file__).parent.parent.parent / "output" / "expected_omop_models.py"
        )
        with open(output_file, "w") as f:
            f.write("\n".join([OMOP_MODULE_HEADER, *all_code_lines]))
        sa_output_file = (
            Path(__file__).parent.parent.parent
            / "output"
            / "expected_sa_omop_models.py"
        )
        with open(sa_output_file, "w") as f:
            f.write("\n".join([SA_OMOP_MODULE_HEADER, *all_sa_code_lines]))

        if error_messages:
            for msg in error_messages:
                print(msg)
            raise AssertionError(
                "Model specification validation failed. See printed messages."
            )
