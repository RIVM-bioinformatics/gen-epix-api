from types import NoneType, UnionType
from typing import Any, Callable, Type, Union

from typing_extensions import Annotated, get_args, get_origin

from gen_epix.fastapp.domain.key import Key
from gen_epix.fastapp.domain.link import Link


def create_keys(keys: dict[int, Key | str | tuple | Callable]) -> dict[int, Key]:
    retval = {}
    for x, y in keys.items():
        if isinstance(y, Key):
            retval[x] = y
        else:
            retval[x] = Key(y)
    return retval


def create_links(
    links: dict[int, Link | tuple[str, Type, str | None]],
) -> dict[int, Link]:
    retval = {}
    for x, y in links.items():
        if isinstance(y, Link):
            retval[x] = y
        else:
            retval[x] = Link(
                link_field_name=y[0],
                link_model_class=y[1],
                relationship_field_name=y[2],
            )
    return retval


def get_type_from_annotation(
    annotation: Type[Any] | None,
) -> Type:
    """
    Adapted from https://github.com/fastapi/sqlmodel v0.0.24
    """
    # Resolve Optional fields
    if annotation is None:
        raise ValueError("Missing field type")
    origin = get_origin(annotation)
    if origin is None:
        return annotation
    elif origin is Annotated:
        return get_type_from_annotation(get_args(annotation)[0])
    if origin is UnionType or origin is Union:
        bases = get_args(annotation)
        if len(bases) > 2:
            raise ValueError("Field type is a non-optional union")
        # Non optional unions are not allowed
        assert len(bases) == 2
        if bases[0] is not NoneType and bases[1] is not NoneType:
            raise ValueError("Field type is a non-optional union")
        # Optional unions are allowed
        use_type = bases[0] if bases[0] is not NoneType else bases[1]
        return get_type_from_annotation(use_type)
    return origin  # type:ignore[no-any-return]
