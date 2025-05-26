import gzip
import hashlib
import io
import json
import os
import pickle
from pathlib import Path
from typing import Any
from uuid import UUID
from zipfile import ZipFile

import pandas as pd
from Bio import SeqIO

from gen_epix.seqdb.domain import enum, model
from util.util import generate_ulid

CURR_DB_FILE = Path.cwd() / "seqdb" / "data" / "load" / "seqdb.dict.seq.full.pkl.gz"

ALLELE_FILES = [
    {
        "id": "019570fd-4652-0464-0cba-8d0ee0f4b304",
        "locus_set_id": UUID("019570fd-4652-0464-0cba-8d0ee0f4b304"),
        "path": Path.cwd()
        / "util"
        / "data"
        / "alleles.019570fd-4652-0464-0cba-8d0ee0f4b304.zip",
    }
]

ALLELE_PROFILE_FILES = [
    {
        "locus_set_id": UUID("019570fd-4652-0464-0cba-8d0ee0f4b304"),
        "locus_detection_protocol_id": UUID("019570fd-4652-5e12-2176-f881c22276b0"),
        "quality_threshold": {
            enum.QualityControlResult.PASS: 0.95,
            enum.QualityControlResult.WARN: 0.90,
        },
        "path": Path.cwd()
        / "util"
        / "data"
        / "allele_profiles.019570fd-4652-0464-0cba-8d0ee0f4b304.csv",
        "allele_file_id": "019570fd-4652-0464-0cba-8d0ee0f4b304",
        "sep": ";",
        "out_path": Path.cwd() / "util" / "data",
        "out_file_prefix": "seqdb.src.",
    }
]


def parse_alleles() -> None:
    """
    Create a table with one allele per row and with columns locus_set_id, locus_code,
    allele_code, allele_id, seq_hash_sha256.
    """
    tgt_file = os.path.join(os.getcwd(), "util", "data", "alleles.pkl.gz")
    # Go over each allele file
    # dfs = []
    for file_data in ALLELE_FILES:
        src_file = file_data["path"]
        allele_count = 0
        locus_allele_map = {}
        # Open zip file and read each containing fasta file
        with ZipFile(src_file, "r") as zip_handle:
            for file_info in zip_handle.infolist():
                with io.TextIOWrapper(zip_handle.open(file_info)) as handle:
                    locus_code = file_info.filename.split(".")[0]
                    # Read fasta file for locus
                    for record in SeqIO.parse(handle, "fasta"):
                        allele_count += 1
                        if (allele_count - 1) % 1000000 == 0:
                            print(f"Processed alleles: {allele_count}")
                        allele_code = record.id
                        allele_seq = str(record.seq).lower()
                        allele_id = generate_ulid()
                        # Calculate SHA256 hash of allele_seq encoded as ASCII
                        allele_seq_hash = hashlib.sha256(
                            allele_seq.encode("ascii")
                        ).digest()
                        # Add allele to rows
                        locus_allele_map[(locus_code, allele_code)] = (
                            allele_id,
                            allele_seq_hash,
                        )
    pickle.dump(locus_allele_map, gzip.open(tgt_file, "wb"))


def parse_allele_profiles() -> None:
    allele_profile_rows = []
    db = pickle.load(gzip.open(CURR_DB_FILE))
    extra_db: dict[str, dict[str, Any]] = {
        "seq.seq": {},
        "seq.allele": {},
        "seq.allele_profile": {},
    }
    allele_id_map = {(x, y.seq_hash_sha256): x for x, y in db[model.Allele].items()}
    allele_id_map = {}
    for i, file_data in enumerate(ALLELE_PROFILE_FILES):
        file_path = file_data["path"]
        allele_file_path = [
            x["path"] for x in ALLELE_FILES if x["id"] == file_data["allele_file_id"]
        ][0]
        locus_set_id = file_data["locus_set_id"]
        locus_detection_protocol_id = file_data["locus_detection_protocol_id"]
        if locus_set_id not in db[model.LocusSet]:
            raise ValueError(f"File {file_path}: locus_set_id does not exist")
        if locus_detection_protocol_id not in db[model.LocusDetectionProtocol]:
            raise ValueError(
                f"File {file_path}: locus_detection_protocol_id does not exist"
            )
        quality_threshold = file_data["quality_threshold"]
        # Read data and keep only rows with dm.include=True
        df = pd.read_csv(file_path, sep=file_data["sep"])
        df.drop(index=df.index[~df["dm.include"]], inplace=True)
        df.set_index("allele_profile_id", drop=False, inplace=True)
        # Create any additional sequences
        seq_ids = df["seq_id"]
        seq_ids_set = set(seq_ids)
        seq_ids_set.difference_update({x for x in seq_ids_set if pd.isna(x)})
        if len(seq_ids_set) < len(seq_ids):
            raise ValueError(
                f"File {file_path}: contains NaN or non-unique seq_id values"
            )
        seq_ids_set = {UUID(x) for x in seq_ids_set}
        extra_db["seq.seq"].update(
            {x: {"id": x, "dm.include": True} for x in seq_ids_set}
        )
        # Check loci
        locus_set: model.LocusSet = db[model.LocusSet][locus_set_id]
        locus_ids = locus_set.locus_ids
        n_loci_in_set = len(locus_ids)
        locus_codes = [db[model.Locus][x].code for x in locus_ids]
        missing_locus_codes = set(locus_codes) - set(df.columns)
        if missing_locus_codes:
            raise ValueError(
                f"File {file_path}: missing locus codes: {missing_locus_codes}"
            )
        profile_df = df.loc[:, locus_codes].fillna(0).astype(int)
        # Extract alleles
        locus_allele_code_id_map = {}
        curr_allele_keys = set(allele_id_map.keys())
        locus_count = 0
        with ZipFile(allele_file_path, "r") as zip_handle:
            for locus_id, locus_code in zip(locus_ids, locus_codes):
                locus_count += 1
                if (locus_count - 1) % 100 == 0:
                    print(f"File {file_path}: processed loci: {locus_count}")
                allele_codes_int_set = set(profile_df[locus_code])
                allele_codes_int_set.discard(0)
                allele_codes = {str(x) for x in allele_codes_int_set}
                allele_map = _retrieve_allele_subset(
                    zip_handle, allele_id_map, locus_code, locus_id, allele_codes
                )
                allele_keys = set(allele_map.keys())
                new_allele_keys = list(allele_keys - curr_allele_keys)
                if new_allele_keys:
                    new_allele_data = {
                        y[0]: {
                            "id": y[0],
                            "locus_id": x[0],
                            "seq_hash_sha256": y[3].hex(),
                            "length": len(y[2]),
                            "seq": y[2],
                            "dm.include": True,
                        }
                        for x, y in allele_map.items()
                        if x in new_allele_keys
                    }
                    extra_db["seq.allele"].update(new_allele_data)
                    locus_allele_code_id_map.update(
                        {
                            (locus_code, y[1]): y[0]
                            for x, y in allele_map.items()
                            if x in new_allele_keys
                        }
                    )
        if locus_count != n_loci_in_set:
            raise ValueError(f"File {file_path}: has different number of loci")
        # Create allele profiles
        allele_profile_id_to_seq_id = {
            x: y for x, y in zip(df["allele_profile_id"], df["seq_id"])
        }
        profile_df = profile_df.transpose()
        allele_profile_count = 0
        for allele_profile_id, allele_codes in profile_df.items():
            allele_profile_count += 1
            if (allele_profile_count - 1) % 100 == 0:
                print(
                    f"File {file_path}: processed allele profiles: {allele_profile_count}"
                )
            allele_profile = [
                locus_allele_code_id_map[(x, str(y))] if y != 0 else None
                for x, y in zip(locus_codes, allele_codes)
            ]
            n_loci_found = sum(x is not None for x in allele_profile)
            # Calculate quality as proportion of loci found
            quality_score = n_loci_found / n_loci_in_set
            quality = (
                enum.QualityControlResult.PASS
                if quality_score >= quality_threshold[enum.QualityControlResult.PASS]
                else (
                    enum.QualityControlResult.WARN
                    if quality_score
                    >= quality_threshold[enum.QualityControlResult.WARN]
                    else enum.QualityControlResult.FAIL
                )
            )
            # Calculate SHA256 hash of allele_profile
            allele_profile_hash_sha256 = (
                model.AlleleProfile.get_allele_profile_hash_sha256(allele_profile)
            )
            allele_profile_rows.append(
                {
                    "id": allele_profile_id,
                    "seq_id": allele_profile_id_to_seq_id[allele_profile_id],
                    "locus_set_id": locus_set_id,
                    "locus_detection_protocol_id": locus_detection_protocol_id,
                    "n_loci": n_loci_found,
                    "allele_profile": json.dumps(
                        [str(x) for x in allele_profile], separators=(",", ":")
                    ),
                    "allele_profile_format": enum.AlleleProfileFormat.SORTED_ALLELE_IDS.value,
                    "allele_profile_hash_sha256": allele_profile_hash_sha256.hex(),
                    "quality_score": quality_score,
                    "quality": quality.value,
                    "dm.include": True,
                },
            )
    extra_db["seq.allele_profile"] = {x["id"]: x for x in allele_profile_rows}
    # Convert db to text files
    prefix = file_data["out_file_prefix"]
    file_path = file_data["out_path"]
    for tbl_name in ["seq.seq", "seq.allele", "seq.allele_profile"]:
        df = pd.DataFrame.from_records(list(extra_db[tbl_name].values()))
        file = file_path / f"{prefix}{tbl_name}.{i+1}.tsv"
        df.to_csv(file, index=False, sep="\t")
        # Convert file to gzip
        with open(file, "rb") as f_in, gzip.open(f"{file}.gz", "wb") as f_out:
            f_out.writelines(f_in)


def _retrieve_allele_subset(
    zip_handle: ZipFile,
    curr_allele_id_map: dict[tuple[UUID, str], UUID],
    locus_code: str,
    locus_id: UUID,
    allele_codes: list[str],
) -> dict[tuple[UUID, str], tuple[UUID, str, str, bytes]]:
    """
    Returns a dict[(locus_id, allele_seq_hash), [allele_id, allele_code, allele_seq, allele_seq_hash]].
    """
    file_name = locus_code + ".fasta"
    has_allele_map = {x: False for x in allele_codes}
    allele_map = {}
    with io.TextIOWrapper(zip_handle.open(file_name)) as handle:
        # Read fasta file for locus
        for record in SeqIO.parse(handle, "fasta"):
            allele_code = record.id
            if allele_code not in has_allele_map:
                continue
            allele_seq = str(record.seq).lower()
            # Calculate SHA256 hash of allele_seq encoded as ASCII
            allele_seq_hash = hashlib.sha256(allele_seq.encode("ascii")).digest()
            has_allele_map[allele_code] = True
            allele_id = curr_allele_id_map.get((locus_id, allele_code), generate_ulid())
            allele_map[(locus_id, allele_seq_hash)] = (
                allele_id,
                allele_code,
                allele_seq,
                allele_seq_hash,
            )
    if any(not x for x in has_allele_map.values()):
        missing_allele_codes_str = ",".join(
            [x for x in has_allele_map if not has_allele_map[x]]
        )
        raise ValueError(
            f"File {file_name}: missing allele codes: {missing_allele_codes_str}"
        )
    return allele_map
