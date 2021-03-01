import logging
import random

from autodjbackend import models


logger = logging.getLogger(__name__)


KEYWORDS = [
    'river',
    'love',
    'blues',
    'party',
    'time',
    'tonight',
    'rain',
    'morning',
    'breathe',
    'fire',
    'woman',
    'disco',
    'rock',
    'music',
    'dancin',
    'baby',
    'twist',
    'lonely',
    'stop',
    'boogie',
    'christmas',
    'moon',
]

ATTR_TO_REL = {
    'position': 'same_track_number',
    'original_artist': 'same_original_artist',
    'year': 'same_year',
    'keyword_in_title': 'keyword_in_title',
}

THREE_MINUTES_IN_MILLISECONDS = 180000
THIRTY_SECONDS_IN_MILLISCEONDS = 30000


def generate(seed_nodes, criteria, total_duration):
    heuristic_dict = {}
    current_track = random.choice(seed_nodes)
    current_total = current_track.duration
    playlist = [current_track]
    time_left = True
    while time_left:
        # Clear existing heuristic values
        heuristic_dict.clear()

        # Get link nodes which connect to all related tracks.
        link_nodes = _get_link_nodes(current_track)

        # Get tracks related to these link nodes
        related_tracks = _get_related_tracks_from_link_nodes(link_nodes)

        # Main loop
        for track in related_tracks:
            heuristic_dict[track.uuid] = _calculate_heuristic_value(
                criteria, current_track, playlist,
                track, total_duration, current_total
            )

        # Bucket tracks accoriding to H-Value
        h_buckets = _bucket_tracks_by_h_value(heuristic_dict)

        next_track = _get_next_track(h_buckets)

        playlist.append(next_track)
        current_total += next_track.duration

        time_left = _is_time_remaining(total_duration, current_total)

    playlist = [track.serialize for track in playlist]

    response = {
        'tracks': playlist,
        'total_duration': current_total
    }

    return response


def _is_time_remaining(total_duration, current_total):
    time_left = True
    time_remaining = total_duration - current_total
    if time_remaining < THIRTY_SECONDS_IN_MILLISCEONDS:
        time_left = False

    return time_left


def _get_next_track(h_buckets):
    best_h_value = max(h_buckets.keys())

    # Pick next track randomly from those with best H-Value
    next_track_uuid = random.choice(h_buckets[best_h_value])
    next_track = models.Track.nodes.get(uuid=next_track_uuid)
    return next_track


def _bucket_tracks_by_h_value(heuristic_dict):
    h_buckets = {}

    for uuid, h_value in heuristic_dict.items():
        try:
            h_buckets[h_value].append(uuid)
        except KeyError:
            h_buckets[h_value] = [uuid]

    return h_buckets


def _calculate_heuristic_value(
    criteria, current_track, playlist, track, total_duration, current_total
):
    h_value = 0

    for key, value in criteria.items():
        if getattr(track, key) == value:
            h_value += 10

    if (
        'original_artist' in criteria.keys() and
        track.artist == track.original_artist
    ):
        h_value -= 5

    # +5 for attributes which directly match current track
    if track.position == current_track.position:
        h_value += 5
    if track.original_artist == current_track.original_artist:
        h_value += 5
    if track.year == current_track.year:
        h_value += 5

    for keyword in KEYWORDS:
        if keyword in track.title and keyword in current_track.title:
            h_value += 5

    if track in playlist:
        h_value = 0

    # Check if time check is needed
    time_remaining = total_duration - current_total

    if time_remaining < THREE_MINUTES_IN_MILLISECONDS:
        tmp_total = current_total + track.duration
        distance_from_zero = abs(total_duration - tmp_total)
        if distance_from_zero < THREE_MINUTES_IN_MILLISECONDS:
            h_value += 5

    return h_value


def _get_related_tracks_from_link_nodes(link_nodes):
    related_tracks = []

    for key in link_nodes.keys():
        related_tracks.extend(getattr(link_nodes[key], key).all())

    return related_tracks


def _get_link_nodes(current_track):
    link_nodes = {}

    for rel in ATTR_TO_REL.values():
        try:
            link_nodes[rel] = getattr(current_track, rel).all()[0]
        except IndexError:
            logger.debug(f'Missing key: {rel}')

    return link_nodes
