import gzip
import os
import pickle
import sys

import pandas as pd

from util.util import generate_ulid

sys.path.append(os.path.join(os.getcwd()))

db_file_name = os.path.join(os.getcwd(), "data/CASEDB - Reference data.pkl.gz")
out_excel_file_name = os.path.join(
    os.getcwd(), "data/CASEDB - Reference data.extra_case_type_set_members.xlsx"
)


def get_db(db_file_name):
    with gzip.open(db_file_name, "rb") as handle:
        retval = pickle.load(handle)
    return retval["mdb"], retval["db"]


mdb, db = get_db(db_file_name)


def get_additional_case_type_set_members_through_etiology(db):
    # Get relevant tables and rename or drop relevant columns
    # Suffix 'a' are tables for generating case_types
    # under case_type_set category EPIDEMIOLOGY, 'b' under MICROBIOLOGY
    df1 = db["ref.case_type_set"].rename(
        columns={"id": "case_type_set_id", "name": "case_type_set_name"}
    )
    df1a = df1.loc[df1["category"] == "EPIDEMIOLOGY", :][
        ["case_type_set_id", "case_type_set_name", "category"]
    ]
    df1b = df1.loc[df1["category"] == "MICROBIOLOGY", :][
        ["case_type_set_id", "case_type_set_name", "category"]
    ]
    df2 = db["ref.case_type_set_member"][["case_type_set_id", "case_type_id"]]
    df3 = db["ref.case_type"].rename(
        columns={"id": "case_type_id", "name": "case_type_name"}
    )[["case_type_id", "case_type_name", "disease_id", "etiological_agent_id"]]
    df3a = df3.loc[~df3["disease_id"].isna(), :].drop(columns="etiological_agent_id")
    df3b = df3.loc[~df3["etiological_agent_id"].isna(), :].drop(columns="disease_id")
    df4 = db["ref.etiology"][["disease_id", "etiological_agent_id"]]
    df5a = db["ref.etiological_agent"].rename(
        columns={"id": "etiological_agent_id", "name": "etiological_agent_name"}
    )[["etiological_agent_id", "etiological_agent_name"]]
    df5b = db["ref.disease"].rename(
        columns={"id": "disease_id", "name": "disease_name"}
    )[["disease_id", "disease_name"]]

    # Generate all case_type_set members for EPIDEMIOLOGY
    # case_type_sets that are etiological_agents
    df7a = (
        df1a.merge(df2, on="case_type_set_id", how="inner")
        .merge(df3a, on="case_type_id", how="inner")
        .merge(df4, on="disease_id", how="inner")
        .merge(df3, on="etiological_agent_id", how="inner", suffixes=("", "_new"))
        .merge(df5a, on="etiological_agent_id", how="inner")
    ).set_index(["case_type_set_id", "case_type_id_new"], drop=False)
    # Generate all case_type_set members for MICROBIOLOGY
    # case_type_sets that are diseases
    df7b = (
        df1b.merge(df2, on="case_type_set_id", how="inner")
        .merge(df3b, on="case_type_id", how="inner")
        .merge(df4, on="etiological_agent_id", how="inner")
        .merge(df3, on="disease_id", how="inner", suffixes=("", "_new"))
        .merge(df5b, on="disease_id", how="inner")
    ).set_index(["case_type_set_id", "case_type_id_new"], drop=False)

    # Add any new case_type_set_members
    df2 = df2.set_index(["case_type_set_id", "case_type_id"])
    df = pd.concat([df7a, df7b])
    df = df.drop(index=[x for x in df.index if x in df2.index]).drop_duplicates()
    df["id"] = [generate_ulid() for i in range(df.shape[0])]
    df = (
        df[
            [
                "id",
                "case_type_set_id",
                "case_type_set_name",
                "case_type_id_new",
                "case_type_name_new",
            ]
        ]
        .rename(
            columns={
                "case_type_id_new": "case_type_id",
                "case_type_name_new": "case_type_name",
            }
        )
        .reset_index(drop=True)
    )
    return df


# Get mdb and db
mdb, db = get_db(db_file_name)

# Generate additional case_type_set_members through etiology,
# e.g. HIV pos. first defined as first, now also as sexually transmitted
df = get_additional_case_type_set_members_through_etiology(db)
df.to_excel(
    out_excel_file_name, sheet_name="ref.case_type_set_member.extra", index=False
)
