import os
import neomodel


from autodjbackend.models import Track


INPUT_PATH = './mbdump/scrubbed_data.csv'
CHUNK_SIZE = 10000


def strip_newlines(attr):
    return attr.replace('\n', '')


def split_line_to_dict(split_line):
    return {
        'title': strip_newlines(split_line[0]),
        'duration': int(split_line[1]),
        'artist': strip_newlines(split_line[2]),
        'album': strip_newlines(split_line[3]),
        'year': int(split_line[4]),
        'position': int(split_line[5]),
        'original_artist': strip_newlines(split_line[6]),
    }


def should_convert(track_params):
    return (
        track_params['title'].isascii() and
        track_params['duration'] > 0 and
        track_params['artist'].isascii() and
        track_params['year'] > 1960 and
        track_params['position'] > 0 and
        track_params['original_artist'].isascii()
    )


def track_equals_dict(track_model: Track, track_dict: dict) -> bool:
    return (
        track_model.title == track_dict['title'] and
        track_model.artist == track_dict['artist'] and
        track_model.year == track_dict['year'] and
        track_model.album == track_dict['album'] and
        track_model.position == track_dict['position'] and
        track_model.original_artist == track_dict['original_artist']
    )


if __name__ == '__main__':
    bolt_url = os.environ.get(
        'NEO4J_BOLT_URL', 'bolt://neo4j:password@db:7687'
    )

    print('Connecting to db')
    neomodel.db.set_connection(bolt_url)

    imported_data = []

    print('Starting file-read.')
    with open(INPUT_PATH, 'r') as file:
        imported_data.extend(file.readlines())
    print('File read complete.')
    imported_data = set(imported_data)

    csv_tracks = {}
    print('Converting to models.')
    for line in imported_data:
        split_line = line.split(',')
        if len(split_line) != 7:
            continue
        track_params = split_line_to_dict(split_line)
        if not should_convert(track_params):
            continue

        key_string = (
            f'{track_params["title"]}{track_params["artist"]}'
            f'{track_params["year"]}{track_params["album"]}'
            f'{track_params["position"]}{track_params["original_artist"]}'
        )

        csv_tracks[key_string] = track_params["duration"]

        if len(csv_tracks) % 10000 == 0:
            print(f'{len(csv_tracks)} parsed.')

    del imported_data

    print(f'CSV Tracks Parsed. Total: {len(csv_tracks)}')

    print('Starting DB qeury now')

    get_all_tracks = 'MATCH (t:Track) WHERE NOT exists(t.duration) RETURN t'

    results, _ = neomodel.db.cypher_query(get_all_tracks)
    print('DB Tracks fetched. Inflating now.')
    db_tracks = [Track.inflate(row[0]) for row in results]

    print(f'DB Tracks converted. Total: {len(db_tracks)}')

    print(
        f'Cleaning complete. New total: {len(db_tracks)}. Starting update now.'
    )

    neomodel.db.begin()
    total_db_tracks = 0
    for track_model in db_tracks:
        key_string = (
            f'{track_model.title}{track_model.artist}'
            f'{track_model.year}{track_model.album}'
            f'{track_model.position}{track_model.original_artist}'
        )

        track_model.duration = csv_tracks[key_string]
        track_model.save()
        del csv_tracks[key_string]
        total_db_tracks += 1

        if total_db_tracks % CHUNK_SIZE == 0:
            neomodel.db.commit()
            print(f'Total: {total_db_tracks}/{len(db_tracks)}')
            neomodel.db.begin()

    neomodel.db.commit()

    print('Process complete.')
