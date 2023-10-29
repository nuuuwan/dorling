from gig import Ent, EntType


def get_config_for_type(ent_type: EntType) -> list[dict]:
    ents = Ent.list_from_type(ent_type)
    return list(
        map(
            lambda d: dict(name=d.name, centroid=d.centroid, color="maroon"),
            ents,
        )
    )
