import json
import os
import sqlite3
from uuid import UUID

import pandas as pd
from ete4 import NCBITaxa

from util.util import generate_ulid

SPECIAL_NO_RANK_TAXIDS = [
    ("root", 1),
    ("cellular organisms", 131567),
]

SELECTED_GENERA = [
    ("Acanthamoeba", 5754),
    ("Acinetobacter", 469),
    ("Alphainfluenzavirus", 197911),
    ("Alphapapillomavirus", 333750),
    ("Alphavirus", 11019),
    ("Anaplasma", 768),
    ("Arenavirus", 11618),
    ("Babesia", 5864),
    ("Bacillus", 1386),
    ("Bartonella", 773),
    ("Betacoronavirus", 694002),
    ("Betainfluenzavirus", 197912),
    ("Betapapillomavirus", 333922),
    ("Bordetella", 517),
    ("Borrelia", 138),
    ("Brucella", 234),
    ("Campylobacter", 194),
    ("Candida", 5475),
    ("Chlamydia", 810),
    ("Citrobacter", 544),
    ("Clostridium", 1485),
    ("Corynebacterium", 1716),
    ("Coxiella", 776),
    ("Cronobacter", 413496),
    ("Cryptosporidium", 5806),
    ("Deltainfluenzavirus", 1511083),
    ("Ebolavirus", 186536),
    ("Echinococcus", 6209),
    ("Enterobacter", 547),
    ("Enterococcus", 1350),
    ("Enterovirus", 12059),
    ("Escherichia", 561),
    ("Flavivirus", 11051),
    ("Francisella", 262),
    ("Fukuyoa", 2022476),
    ("Gambierdiscus", 373097),
    ("Gammainfluenzavirus", 197913),
    ("Gammapapillomavirus", 325455),
    ("Giardia", 5740),
    ("Haemophilus", 724),
    ("Hafnia", 568),
    ("Helicobacter", 209),
    ("Henipavirus", 260964),
    ("Hepatovirus", 12091),
    ("Klebsiella", 570),
    ("Legionella", 445),
    ("Leishmania", 5658),
    ("Lentivirus", 11646),
    ("Leptospira", 171),
    ("Listeria", 1637),
    ("Lyssavirus", 11286),
    ("Mammarenavirus", 1653394),
    ("Marburgvirus", 186537),
    ("Moraxella", 475),
    ("Morbillivirus", 11229),
    ("Morganella", 581),
    ("Mupapillomavirus", 334202),
    ("Mycobacterium", 1763),
    ("Neisseria", 482),
    ("Norovirus", 142786),
    ("Nupapillomavirus", 475861),
    ("Orthobunyavirus", 11572),
    ("Orthoflavivirus", 3044782),
    ("Orthohantavirus", 1980442),
    ("Orthonairovirus", 1980517),
    ("Orthopoxvirus", 10242),
    ("Orthorubulavirus", 2560195),
    ("Pantoea", 53335),
    ("Phlebovirus", 11584),
    ("Plasmodium", 5820),
    ("Proteus", 583),
    ("Providencia", 586),
    ("Pseudomonas", 286),
    ("Rickettsia", 780),
    ("Rotavirus", 10912),
    ("Rubivirus", 11040),
    ("Salmonella", 590),
    ("Serratia", 613),
    ("Shigella", 620),
    ("Simplexvirus", 10294),
    ("Staphylococcus", 1279),
    ("Stenotrophomonas", 40323),
    ("Streptococcus", 1301),
    ("Toxoplasma", 5810),
    ("Treponema", 157),
    ("Trichinella", 6333),
    ("Varicellovirus", 10319),
    ("Variola", 300414),
    ("Vibrio", 662),
    ("Yersinia", 629),
]

EXTRA_TAXA = [
    ("Severe acute respiratory syndrome coronavirus 2", 2697049),
]

RANK_MAP = {
    "no rank": "NO_RANK",
    "domain": "DOMAIN",
    "superkingdom": "SUPERKINGDOM",
    "kingdom": "KINGDOM",
    "subkingdom": "SUBKINGDOM",
    "phylum": "PHYLUM",
    "subphylum": "SUBPHYLUM",
    "superclass": "SUPERCLASS",
    "class": "CLASS",
    "subclass": "SUBCLASS",
    "infraclass": "INFRACLASS",
    "order": "ORDER",
    "suborder": "SUBORDER",
    "family": "FAMILY",
    "subfamily": "SUBFAMILY",
    "genus": "GENUS",
    "subgenus": "SUBGENUS",
    "species group": "SPECIES_GROUP",
    "species subgroup": "SPECIES_SUBGROUP",
    "species": "SPECIES",
    "subspecies": "SUBSPECIES",
    "strain": "STRAIN",
    "clade": "CLADE",
    "tribe": "TRIBE",
}


def update_ncbi_taxonomy(update_database: bool = False) -> None:
    # Use ete package to download and parse NCBI taxonomy
    ncbi = NCBITaxa()
    if update_database:
        ncbi.update_taxonomy_database()


def read_ncbi_taxonomy() -> pd.DataFrame:
    # Retrieve data from sqlite database with NCBI taxonomy created by ete package
    file = os.path.join(os.environ["XDG_DATA_HOME"], "ete", "taxa.sqlite")
    conn = sqlite3.connect(file)
    ncbi_df = pd.read_sql_query("SELECT * FROM species", conn)
    conn.close()
    # Split track into list of taxids
    ncbi_df["track"] = ncbi_df["track"].apply(lambda x: [int(y) for y in x.split(",")])
    ncbi_df["track_set"] = ncbi_df["track"].apply(frozenset)
    # Map rank
    ncbi_df["rank"] = ncbi_df["rank"].map(RANK_MAP)
    # Set index to taxid and sort by it
    ncbi_df.set_index("taxid", drop=False, inplace=True)
    ncbi_df.sort_index(axis=0, inplace=True)
    return ncbi_df


def get_ncbi_taxon_subset(ncbi_df: pd.DataFrame) -> None:
    # Identify species as those belonging to a genus in GENERA
    genus_taxids = frozenset(x[1] for x in SELECTED_GENERA)
    ncbi_df["is_matching_species"] = (ncbi_df["rank"] == "SPECIES") & ncbi_df[
        "track_set"
    ].apply(lambda x: any(y in genus_taxids for y in x))
    # Identify additional taxa
    extra_taxids = frozenset(x[1] for x in EXTRA_TAXA)
    ncbi_df["is_matching_extra"] = ncbi_df["taxid"].isin(extra_taxids)
    # Identify taxa that are ancestors of the identified species or extra taxa
    ancestor_taxids = set.union(
        set(),
        ncbi_df[ncbi_df["is_matching_extra"]]["taxid"].tolist(),
        *ncbi_df[ncbi_df["is_matching_species"]]["track_set"].tolist(),
    )
    ncbi_df["is_matching_ancestor"] = ncbi_df["taxid"].isin(ancestor_taxids)
    mask = (
        ncbi_df["is_matching_species"]
        | ncbi_df["is_matching_extra"]
        | ncbi_df["is_matching_ancestor"]
    )
    ncbi_df.drop(ncbi_df.index[~mask], inplace=True)
    # Remove taxa that are unclassified, selected having a "no rank" ancestor,
    # excluding special and extra cases
    extra_ancestor_taxids = set.union(
        set(),
        *ncbi_df[ncbi_df["is_matching_extra"]]["track_set"].tolist(),
    )
    excluded_taxids = (
        set(ncbi_df.loc[ncbi_df["rank"] == "NO_RANK", "taxid"])
        - extra_ancestor_taxids
        - {x[1] for x in SPECIAL_NO_RANK_TAXIDS}
    )
    ncbi_df["is_unclassified_taxon"] = ncbi_df["track"].apply(
        lambda x: any(y in excluded_taxids for y in x)
    )
    ncbi_df.drop(ncbi_df.index[ncbi_df["is_unclassified_taxon"]], inplace=True)
    # # TODO: Temporary write out to facilitate debugging
    # ncbi_df.to_pickle(os.path.join(os.environ["XDG_DATA_HOME"], "ncbi_taxonomy.pkl"))
    # ncbi_df.to_excel(
    #     os.path.join(os.environ["XDG_DATA_HOME"], "ncbi_taxonomy.xlsx"),
    #     sheet_name="ncbi_taxonomy",
    # )


def retrieve_seqdb_taxon(file: str) -> pd.DataFrame:
    if not os.path.exists(file):
        seqdb_df = pd.DataFrame.from_dict(
            {
                "id": pd.Series([], dtype=object),
                "code": pd.Series([], dtype=str),
                "name": pd.Series([], dtype=str),
                "rank": pd.Series([], dtype=str),
                "ncbi_taxid": pd.Series([], dtype="Int64"),
                "ictv_ictv_id": pd.Series([], dtype=str),
                "snomed_sctid": pd.Series([], dtype="Int64"),
                "subtyping_scheme_id": pd.Series([], dtype=str),
                "subtyping_scheme": pd.Series([], dtype=object),
                "ncbi_ancestor_taxids": pd.Series([], dtype=object),
                "ancestor_taxon_ids": pd.Series([], dtype=object),
                "dm.include": pd.Series([], dtype=bool),
                "dm.include_row": pd.Series([], dtype=bool),
            },
            orient="columns",
        )
    else:
        seqdb_df = pd.read_csv(
            file,
            sep="\t",
            dtype={
                "id": object,
                "code": str,
                "name": str,
                "rank": str,
                "ncbi_taxid": "Int64",
                "ictv_ictv_id": str,
                "snomed_sctid": "Int64",
                "subtyping_scheme_id": str,
                "subtyping_scheme": object,
                "ncbi_ancestor_taxids": object,
                "ancestor_taxon_ids": object,
                "dm.include": bool,
                "dm.include_row": bool,
            },
        )
    seqdb_df["ancestor_taxon_ids"] = seqdb_df["ancestor_taxon_ids"].apply(
        lambda x: [UUID(y) for y in json.loads(x)]
    )
    seqdb_df["ncbi_ancestor_taxids"] = seqdb_df["ncbi_ancestor_taxids"].apply(
        json.loads
    )
    for col_name in seqdb_df.columns:
        mask = pd.isnull(seqdb_df[col_name])
        if mask.any():
            seqdb_df.loc[mask, col_name] = None
    seqdb_df.set_index("ncbi_taxid", drop=False, inplace=True)
    return seqdb_df


def transform_ncbi_to_seqdb(ncbi_df: pd.DataFrame) -> pd.DataFrame:
    n_rows = ncbi_df.shape[0]
    seqdb_df = pd.DataFrame.from_dict(
        {
            "id": pd.Series(
                [generate_ulid() for i in range(n_rows)],
                index=ncbi_df.index,
                dtype=object,
            )
        },
        orient="columns",
    )
    seqdb_df["code"] = ncbi_df["taxid"].apply(lambda x: f"NCBI:txid{x}").astype(str)
    seqdb_df["name"] = ncbi_df["spname"].astype(str)
    seqdb_df["rank"] = ncbi_df["rank"].astype(str)
    seqdb_df["ncbi_taxid"] = ncbi_df["taxid"].astype("Int64")
    seqdb_df["ictv_ictv_id"] = pd.Series(
        [None] * n_rows, index=ncbi_df.index, dtype=str
    )
    seqdb_df["subtyping_scheme_id"] = pd.Series(
        [None] * n_rows, index=ncbi_df.index, dtype=str
    )
    seqdb_df["subtyping_scheme"] = pd.Series(
        [None] * n_rows, index=ncbi_df.index, dtype=str
    )
    seqdb_df["ncbi_ancestor_taxids"] = ncbi_df["track"].astype(object)
    seqdb_df["ancestor_taxon_ids"] = pd.Series(
        [None] * n_rows, index=ncbi_df.index, dtype=object
    )
    seqdb_df["dm.include"] = pd.Series([True] * n_rows, index=ncbi_df.index, dtype=bool)
    seqdb_df["dm.include_row"] = pd.Series(
        [True] * n_rows, index=ncbi_df.index, dtype=bool
    )
    seqdb_df.set_index("ncbi_taxid", drop=False, inplace=True)
    return seqdb_df


def get_seqdb_taxon_changes(
    curr_seqdb_df: pd.DataFrame, ncbi_df: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    created_taxids = sorted(
        list(set(ncbi_df["taxid"]) - set(curr_seqdb_df["ncbi_taxid"]))
    )
    updated_taxids = sorted(
        list(set(ncbi_df["taxid"]) & set(curr_seqdb_df["ncbi_taxid"]))
    )
    deleted_taxids = sorted(
        list(set(curr_seqdb_df["ncbi_taxid"]) - set(ncbi_df["taxid"]))
    )
    created_seqdb_df = transform_ncbi_to_seqdb(ncbi_df.loc[created_taxids, :])
    updated_seqdb_df = transform_ncbi_to_seqdb(ncbi_df.loc[updated_taxids, :])
    updated_seqdb_df["id"] = curr_seqdb_df.loc[updated_taxids, "id"]
    deleted_seqdb_df = curr_seqdb_df.loc[
        curr_seqdb_df["ncbi_taxid"].isin(deleted_taxids), :
    ]
    # Map NCBI to seqdb taxon ids
    ncbi_taxids = (
        created_seqdb_df["ncbi_taxid"].tolist()
        + updated_seqdb_df["ncbi_taxid"].tolist()
        + deleted_seqdb_df["ncbi_taxid"].tolist()
    )
    seqdb_ids = (
        created_seqdb_df["id"].tolist()
        + updated_seqdb_df["id"].tolist()
        + deleted_seqdb_df["id"].tolist()
    )
    ncbi_taxid_seqdb_id_map = {x: y for x, y in zip(ncbi_taxids, seqdb_ids)}
    # Remove identical rows from updated
    if updated_taxids:
        orig_seqdb_df = curr_seqdb_df.loc[updated_taxids, :]
        mask = None
        for col_name in ["code", "name", "rank", "ncbi_ancestor_taxids"]:
            if mask is None:
                mask = updated_seqdb_df[col_name] != orig_seqdb_df[col_name]
            else:
                mask = mask | (updated_seqdb_df[col_name] != orig_seqdb_df[col_name])
        updated_seqdb_df = updated_seqdb_df.loc[mask, :]
    # Fill in ancestor_taxon_ids
    for seqdb_df in [created_seqdb_df, updated_seqdb_df, deleted_seqdb_df]:
        seqdb_df["ancestor_taxon_ids"] = seqdb_df["ncbi_ancestor_taxids"].apply(
            lambda x: [ncbi_taxid_seqdb_id_map[y] for y in x]
        )

    return {
        "CREATED": created_seqdb_df,
        "UPDATED": updated_seqdb_df,
        "DELETED": deleted_seqdb_df,
    }


def parse_ncbi_taxonomy(update_ncbi_database: bool = False) -> None:
    # Create some config data
    seqdb_taxon_file = os.path.join(
        os.getcwd(), "seqdb", "data", "extract", "seqdb.src.seq.taxon.tsv"
    )
    out_files = {
        x: os.path.join(
            os.getcwd(),
            "seqdb",
            "data",
            "extract",
            f"seqdb.src.seq.taxon.{x.lower()}.tsv",
        )
        for x in ["CREATED", "UPDATED", "DELETED"]
    }
    # Retrieve NCBI taxonomy data, parse it, and compare it with the current seqdb taxonomy
    update_ncbi_taxonomy(update_database=update_ncbi_database)
    ncbi_df = read_ncbi_taxonomy()
    get_ncbi_taxon_subset(ncbi_df)
    # # TODO: Temporary read in to facilitate debugging
    # ncbi_df = pd.read_pickle(
    #     os.path.join(os.environ["XDG_DATA_HOME"], "ncbi_taxonomy.pkl")
    # )
    seqdb_df = retrieve_seqdb_taxon(seqdb_taxon_file)
    seqdb_changes = get_seqdb_taxon_changes(seqdb_df, ncbi_df)
    # Write out
    for key, df in seqdb_changes.items():
        df["ancestor_taxon_ids"] = df["ancestor_taxon_ids"].apply(
            lambda x: json.dumps([str(y) for y in x])
        )
        df["ncbi_ancestor_taxids"] = df["ncbi_ancestor_taxids"].apply(json.dumps)
        df.to_csv(out_files[key], index=False, sep="\t", na_rep="")
    # TODO: Temporary write out to facilitate debugging
    # ncbi_df.to_csv(
    #     os.path.join(os.environ["XDG_DATA_HOME"], "ncbi_taxonomy.tsv"),
    #     index=False,
    #     sep="\t",
    # )
