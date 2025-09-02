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
        The base directory where the ERM diagrams will be saved. Subdirectories for each domain will be created under this path.

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

    for name, domain in domains.items():
        generate_erm_diagrams_for_domain(domain, out_dir / "erm" / name)
        generate_erm_diagrams_for_service(domain, out_dir / "erm" / name)


def generate_erm_diagrams_for_domain(domain: Domain, file_root: Path):
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
    None
        This function does not return a value. It saves the ERM diagram as a PNG file.

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
