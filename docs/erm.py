import hashlib
import json
import pickle
import re
from pathlib import Path

import erdantic as erd

from gen_epix.casedb.domain import DOMAIN as CASEDB_DOMAIN
from gen_epix.fastapp import Domain
from gen_epix.omopdb.domain import DOMAIN as OMOPDB_DOMAIN
from gen_epix.seqdb.domain import DOMAIN as SEQDB_DOMAIN


def generate_erm_diagrams(out_dir: Path) -> None:
    """
    Generates Entity-Relationship Model (ERM) diagrams for predefined database domains and their services.

    This function creates an output directory (if it does not exist) and iterates over a set of database domains,
    generating ERM diagrams for each domain and its associated services.

    Parameters
    ----------
    out_dir : Path
        The base directory where the ERM diagrams will be saved.

    Returns
    -------
    None
        This function does not return any value. It performs file system operations and diagram generation as side effects.
    """
    domains = {
        "casedb": CASEDB_DOMAIN,
        "omopdb": OMOPDB_DOMAIN,
        "seqdb": SEQDB_DOMAIN,
    }

    # Create output "erm" directory if it does not exist
    if not Path(out_dir / "erm").is_dir():
        Path.mkdir(out_dir / "erm")

    combined_sorted_model_classes = []
    for name, domain in domains.items():
        file_path_with_prefix = out_dir / "erm" / name
        sorted_model_classes = generate_erm_diagrams_for_domain(
            domain, file_path_with_prefix
        )
        generate_erm_diagrams_for_service(domain, file_path_with_prefix)
        combined_sorted_model_classes.extend(sorted_model_classes)

    pickle_file_path = out_dir / "erm" / "temp_domain_pickle_file.pkl"
    create_domain_pickle_file(combined_sorted_model_classes, pickle_file_path)
    domain_pickle_hash = create_sha256_hash(pickle_file_path)
    hash_dict = create_hash_dict(domain_pickle_hash)
    create_hash_json_file(hash_dict, out_dir / "erm" / "erm.json")
    remove_file(pickle_file_path)


def generate_erm_diagrams_for_domain(domain: Domain, file_root: Path) -> list:
    """
    Generates and saves an Entity-Relationship Model (ERM) diagram for all persistable models in the given domain.

    Parameters
    ----------
    domain : Domain
        The domain object containing model classes to be included in the ERM diagram.
    file_root : Path
        The root path (without extension) where the generated ERM diagram image will be saved.

    Returns
    -------
    list
        A list of sorted model class objects included in the ERM diagram.

    Notes
    -----
    - The output file will be named using the snake_case version of the file_root with a '_domain.png' suffix.
    - Only persistable models are included in the diagram.
    """
    sorted_model_classes = domain.get_dag_sorted_models(persistable=True)
    output_file = camelcase_to_snakecase(f"{file_root}_domain.png")
    erd.draw(
        *sorted_model_classes,
        out=output_file,
        limit_search_models_to=[x.__name__ for x in sorted_model_classes],
    )
    return sorted_model_classes


def generate_erm_diagrams_for_service(domain: Domain, file_root: Path):
    """
    Generates and saves Entity-Relationship Model (ERM) diagrams for each service type in the given domain.

    Parameters
    ----------
    domain : Domain
        The domain object containing service types and their associated models.
    file_root : Path
        The root path or filename prefix for the output ERM diagram files.

    Notes
    -----
    For each service type in the domain, this function retrieves the associated model classes,
    generates an ERM diagram, and saves it as a PNG file. The output filename is constructed
    by combining the file_root and the service type name in snake_case.
    """
    for service_type in domain.get_service_types():
        model_classes = domain.get_models_for_service_type(service_type)
        output_file = camelcase_to_snakecase(f"{file_root}_{service_type}.png")
        erd.draw(
            *model_classes,
            out=output_file,
            limit_search_models_to=[x.__name__ for x in model_classes],
        )


def camelcase_to_snakecase(name: str) -> str:
    """
    Converts a CamelCase string to snake_case.

    This function takes a string in CamelCase format and converts it to snake_case.

    Parameters
    ----------
    name : str
        The CamelCase string to convert. Can include a file extension.

    Returns
    -------
    str
        The converted snake_case string, with the file extension preserved if present.
    """
    pattern = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
    # Replace all "." with "_" except for the file extension
    file, extension = name.rsplit(".", 1)
    file = pattern.sub("_", file).replace(".", "_").lower()
    name = f"{file}.{extension}"
    return name


def create_domain_pickle_file(sorted_model_classes: list, file_path: Path):
    """
    Saves a list of sorted model classes to a pickle file.

    Parameters
    ----------
    sorted_model_classes : list
        A list containing sorted model class objects to be saved.
    file_path : Path
        The path to the file where the pickle data will be written.

    Returns
    -------
    None
        This function does not return anything. It writes the data to the specified file.
    """
    with open(file_path, "wb") as file:
        pickle.dump(sorted_model_classes, file)


def create_sha256_hash(filename: Path) -> str:
    """
    Generates a SHA-256 hash for the contents of a given file.

    Parameters
    ----------
    filename : Path
        The path to the file whose contents will be hashed.

    Returns
    -------
    str
        The SHA-256 hash of the file's contents as a hexadecimal string.
    """
    with open(filename, "rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def create_hash_dict(hash: str) -> dict:
    """
    Create a dictionary containing the provided hash under the key 'Domain model classes'.

    Parameters
    ----------
    hash : str
        The hash string to be stored in the dictionary.

    Returns
    -------
    dict
        A dictionary with a single key 'Domain model classes' and the provided hash as its value.
    """
    return {"Domain model classes": hash}


def create_hash_json_file(hash_dict: dict, file_path: Path):
    """
    Creates a JSON file from a given dictionary of hashes.

    Parameters
    ----------
    hash_dict : dict
        Dictionary containing hash values to be stored in the JSON file.
    file_path : Path
        Path object specifying the location where the JSON file will be created.

    Returns
    -------
    None
        This function does not return anything. It writes the hash dictionary to a JSON file at the specified path.
    """
    with open(file_path, "w") as file:
        json.dump(hash_dict, file)


def remove_file(file_path: Path):
    """
    Removes the specified file from the filesystem.

    Parameters
    ----------
    file_path : Path
        The path to the file to be removed.

    Notes
    -----
    If the specified path does not point to a file, no action is taken.
    """
    if file_path.is_file():
        file_path.unlink()
