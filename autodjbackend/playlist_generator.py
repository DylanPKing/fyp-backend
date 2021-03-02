import logging
import random

from autodjbackend.models import Track
from autodjbackend.track_cache import TrackCache
from autodjbackend.utils import (
    minutes_to_milliseconds, milliseconds_to_minutes
)


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


def generate(seed_nodes, criteria, total_duration):
    """
    Generates a playlist using user criteria, and the given seed nodes.

    This is the main function for generating playlists. It picks one of the
    seed nodes at random to start with, as they all have the same heuristic
    value.

    The main loop of this function traverses the graph to get all of the link
    nodes for the current track, and then retrieves all of the tracks related
    to these link nodes. This emulates retreiving all of the related nodes from
    a graph where the tracks are directly connected.

    Next, each potential track is assigned a heuristic value. THey are then
    bucketed according to their heurstic value. The algorithm then picks one of
    the highest scoring tracks at random, and adds that to the playlist.

    This process repeats until the runtime of the playlist is at least 30
    seconds less than the user-specified runtime.

    Args:
        seed_nodes (list(Track)): A list of tracks that meets user criteria
        criteria (dict()): The users criteria, used by the heuritsic function
        total_duration (int): User-specified runtime in milliseconds.

    Returns:
        dict(): A dict containing serialized tracks, and the total runtime
            in minutes.
    """
    heuristic_dict = {}
    current_track = random.choice(seed_nodes)
    current_total = current_track.duration
    playlist = [current_track]
    logger.info(
        f'Starting track: {current_track.artist}: {current_track.title}'
    )
    time_left = True
    while time_left:
        # Clear existing heuristic values
        heuristic_dict.clear()

        # Get link nodes which connect to all related tracks.
        logger.info('Getting related tracks.')
        related_tracks = _get_related_tracks(current_track)

        # Main loop
        logger.info('Calculating heuristic values.')
        for track in related_tracks:
            if not _h_value_exists(heuristic_dict, track.uuid):
                heuristic_dict[track.uuid] = _calculate_heuristic_value(
                    criteria, current_track, playlist,
                    track, total_duration, current_total
                )

        # Bucket tracks accoriding to H-Value
        h_buckets = _bucket_tracks_by_h_value(heuristic_dict)

        next_track = _get_next_track(h_buckets)

        playlist.append(next_track)
        current_total += next_track.duration

        logger.info(f'Next track: {next_track.artist}: {next_track.title}')
        logger.info(f'Current track count: {len(playlist)}')
        logger.info(
            f'Current runtime: {milliseconds_to_minutes(current_total)}'
        )

        time_left = _is_time_remaining(total_duration, current_total)

    response = {
        'tracks': [track.serialize for track in playlist],
        'total_duration': milliseconds_to_minutes(current_total)
    }

    return response


def _h_value_exists(heurstic_dict, uuid):
    try:
        heurstic_dict[uuid]
    except KeyError:
        return False
    else:
        return True


def _is_time_remaining(total_duration, current_total):
    time_left = True
    time_remaining = total_duration - current_total
    if time_remaining < minutes_to_milliseconds(0.5):
        time_left = False

    return time_left


def _get_next_track(h_buckets):
    best_h_value = max(h_buckets.keys())

    # Pick next track randomly from those with best H-Value
    next_track_uuid = random.choice(h_buckets[best_h_value])
    next_track = Track.nodes.get(uuid=next_track_uuid)
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

    if track not in playlist:
        h_value += _matches_user_criteria(criteria, track)
        h_value += _original_performance(criteria, track)
        h_value += _matches_current_track(current_track, track)
        h_value += _contains_keywords(current_track, track)
        h_value += _check_remaining_time(track, total_duration, current_total)

    return h_value


def _check_remaining_time(track, total_duration, current_total):
    h_value = 0

    three_minutes_in_milliseconds = minutes_to_milliseconds(3)

    time_remaining = total_duration - current_total
    if time_remaining < three_minutes_in_milliseconds:
        tmp_total = current_total + track.duration
        distance_from_zero = abs(total_duration - tmp_total)
        if distance_from_zero < three_minutes_in_milliseconds:
            h_value += 5

    return h_value


def _contains_keywords(current_track, track):
    h_value = 0

    for keyword in KEYWORDS:
        if keyword in track.title and keyword in current_track.title:
            h_value += 5

    return h_value


def _matches_current_track(current_track, track):
    h_value = 0

    if track.position == current_track.position:
        h_value += 5
    if track.original_artist == current_track.original_artist:
        h_value += 5
    if track.year == current_track.year:
        h_value += 5

    return h_value


def _original_performance(criteria, track):
    h_value = 0

    if (
        'original_artist' in criteria.keys() and
        track.artist == track.original_artist
    ):
        h_value -= 5

    return h_value


def _matches_user_criteria(criteria, track):
    h_value = 0
    for key, value in criteria.items():
        if getattr(track, key) == value:
            h_value += 10

    return h_value


def _get_related_tracks(current_track):
    related_tracks = []
    track_cache = TrackCache.get_instance()

    for rel in ATTR_TO_REL.values():
        try:
            link_node = getattr(current_track, rel).all()[0]
        except IndexError:
            logger.debug(f'Missing key: {rel}')
        else:
            try:
                linked_tracks = track_cache.get_tracks_from_link_node(
                    link_node.uuid
                )
            except KeyError:
                linked_tracks = getattr(link_node, rel).all()
                track_cache.add_result_to_cache(link_node.uuid, linked_tracks)

            related_tracks.extend(linked_tracks)

    return related_tracks
