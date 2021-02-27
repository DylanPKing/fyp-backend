INPUT_PATH = './mbdump/data_with_original_artist.csv'
OUTPUT_PATH = './mbdump/scrubbed_data.csv'


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
        track_params['duration'] > 44 and
        track_params['artist'].isascii() and
        track_params['year'] >= 1985 and
        0 < track_params['position'] <= 15 and
        track_params['original_artist'].isascii()
    )


if __name__ == '__main__':
    imported_data = []

    print('Starting file-read.')
    with open(INPUT_PATH, 'r') as file:
        imported_data.extend(file.readlines())
    print('File read complete.')
    imported_data = set(imported_data)

    print(f'Total imported tracks: {len(imported_data)}')

    tracks = []
    print('Converting to models.')
    for line in imported_data:
        split_line = line.split(',')
        if len(split_line) != 7:
            continue
        track_params = split_line_to_dict(split_line)
        if not should_convert(track_params):
            continue
        tracks.append(track_params)
        if len(tracks) % 10000 == 0:
            print(f'{len(tracks)} converted.')

    del imported_data

    print(f'New total: {len(tracks)}')

    print('Writing to file.')
    with open(OUTPUT_PATH, 'w') as file:
        for track in tracks:
            output_string = (
                f"{track['title']},{track['duration']},{track['artist']},"
                f"{track['album']},{track['year']},{track['position']},"
                f"{track['original_artist']}\n"
            )
            file.write(output_string)
