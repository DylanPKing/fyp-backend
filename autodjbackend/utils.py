import logging

from autodjbackend import models


logger = logging.getLogger(__name__)

VALID_CRITERIA = [
    'track_number',
    'year',
    'original_artist',
    'keyword_in_title',
]

CRITERA_TO_NODE_MODEL = {
    'track_number': models.SameTrackNumber.nodes,
    'year': models.SameYear.nodes,
    'original_artist': models.SameOriginalArtist.nodes,
    'keyword_in_title': models.KeywordInTitle.nodes,
}


def get_criteria_to_search(track_criteria):
    criteria_to_search = {}
    for criteria in VALID_CRITERIA:
        try:
            criteria_to_search[criteria] = track_criteria[criteria]
        except KeyError:
            logger.info(f'Criteria not sent by client: {criteria}.')

    return criteria_to_search


def get_link_nodes_from_criteria(criteria_to_search):
    link_nodes = []
    for key, value in criteria_to_search.items():
        link_node_class = CRITERA_TO_NODE_MODEL[key]
        params = {key: value}
        link_node = link_node_class.filter(**params)
        link_nodes.append(link_node)

    return link_nodes
