import re

MLVA_NO_LOCUS_REPEAT_NUMBER = -1
NCBI_TAXID_PATTERN = re.compile(r"^NCBI:txid\d+$")

REQUIRED_NEXTCLADE_KEYS = [
    "substitutions",
    "deletions",
    "insertions",
    "missing",
    "nonACGTNs",
]

REQUIRED_NEXTCLADE_SEQ_KEYS = REQUIRED_NEXTCLADE_KEYS + [
    "alignmentStart",
    "alignmentEnd",
]
NEXTCLADE_SUBSTITUTION_PATTERN = re.compile(r"^[A-Za-z](\d+)([A-Za-z-])$")
NEXTCLADE_INSERTION_PATTERN = re.compile(r"^(\d+):([A-Za-z-]+)$")
NEXTCLADE_NON_ACGTN_PATTERN = re.compile(r"^([A-Za-z-]+):(\d+(?:-\d+)?)$")
NEXTCLADE_POSITION_RANGE_PATTERN = re.compile(r"^(\d+)(?:-(\d+))?$")
