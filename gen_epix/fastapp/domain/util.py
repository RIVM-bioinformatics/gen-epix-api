from typing import Callable, Type

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
