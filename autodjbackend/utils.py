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


def get_seed_nodes_from_criteria(criteria_to_search):
    return models.Track.nodes.filter(**criteria_to_search).all()
