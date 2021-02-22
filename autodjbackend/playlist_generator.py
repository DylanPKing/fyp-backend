from neomodel.core import StructuredNode

from autodjbackend.models import Track


def generate(
    link_nodes: list(StructuredNode), total_duration: int
) -> list(Track):
    # TODO: Heuristic:
    # - Match Specified Criteria: +10
    # - Matches one of non-specified Criteria: +5
    # - if less than 10 mins left of total duration,
    #   bring duration close to 0: +5
    pass
