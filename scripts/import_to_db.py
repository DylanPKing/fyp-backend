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


if __name__ == '__main__':

    bolt_url = os.environ.get(
        'NEO4J_BOLT_URL', 'bolt://neo4j:password@db:7687'
    )

    print('Connecting to db')
    neomodel.db.set_connection(bolt_url)

    # This script is for a fresh db, so clearing any old data.
    print('Clearing db.')
    neomodel.clear_neo4j_database(neomodel.db)

    imported_data = []

    print('Starting file-read.')
    with open(INPUT_PATH, 'r') as file:
        imported_data.extend(file.readlines())
    print('File read complete.')
    imported_data = set(imported_data)

    tracks = []
    print('Converting to models.')
    for line in imported_data:
        split_line = line.split(',')
        if len(split_line) != 7:
            continue
        track_params = split_line_to_dict(split_line)
        if not should_convert(track_params):
            continue
        track = Track(**track_params)
        tracks.append(track)
        if len(tracks) % 10000 == 0:
            print(f'{len(tracks)} converted.')

    del imported_data

    print('Splitting data')
    chunked_data = [
        tracks[i:i+CHUNK_SIZE] for i in range(0, len(tracks), CHUNK_SIZE)
    ]

    print('Starting db commit.')
    i = 0
    for chunk in chunked_data:
        with neomodel.db.write_transaction:
            for track in chunk:
                track.save()
        i += 1
        total_written = i * CHUNK_SIZE
        print(f'Chunk {i} completed. {total_written} tracks written.')

    print('Process complete. If script does not finish execution press Ctrl+C')
