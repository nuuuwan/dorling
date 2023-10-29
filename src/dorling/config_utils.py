import os

from gig import Ent, EntType
from utils import JSONFile


def get_config_for_type(ent_type: EntType) -> list[dict]:
    ents = Ent.list_from_type(ent_type)
    return list(
        map(
            lambda d: dict(name=d.name, centroid=d.centroid, color="maroon"),
            ents,
        )
    )


def get_config_for_countries() -> list[dict]:
    data_list = JSONFile(
        os.path.join('data', 'countries.simpler.json')
    ).read()
    return list(
        map(
            lambda d: dict(
                name=d['alpha3'],
                centroid=d['capital_latlng'],
                color=d['color'],
            ),
            data_list,
        )
    )
