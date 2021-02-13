from autodjbackend.models.track import Track


INPUT_PATH = './mbdump/data_without_covers.csv'
OUTPUT_PATH = './mbdump/data_with_original_artist.csv'


def get_earliest_year(track_list):
    earliest_track = track_list[0]
    for track in track_list:
        if track.year < earliest_track.year:
            earliest_track = track

    return earliest_track


def split_line_to_dict(split_line):
    return {
        'title': split_line[0],
        'duration': int(split_line[1]),
        'artist': split_line[2],
        'album': split_line[3],
        'year': int(split_line[4]),
        'position': int(split_line[5]),
    }


if __name__ == '__main__':
    imported_data = []

    print('Starting file-read.')
    with open(INPUT_PATH, 'r') as file:
        imported_data.extend(file.readlines())
    print('File read complete.')
    imported_data = set(imported_data)

    tracks = []
    print('Converting to model.')
    for line in imported_data:
        split_line = line.split(',')
        if len(split_line) != 7:
            continue
        track_params = split_line_to_dict(split_line)
        track = Track(**track_params)
        tracks.append(track)

    del imported_data

    titles_counts = {}

    print('Bucketing tracks')
    for track in tracks:
        if track.title in titles_counts:
            titles_counts[track.title].append(track)
        else:
            titles_counts[track.title] = [track]

    print('Assigning original artist.')
    for bucket in titles_counts.values():
        original_track = get_earliest_year(bucket)
        for track in bucket:
            track.original_artist = original_track.artist

    data_to_export = []
    for bucket in titles_counts.values():
        data_to_export.extend(bucket)

    print('Writing to file.')
    with open(OUTPUT_PATH, 'w') as file:
        for track in data_to_export:
            output_string = (
                f'{track.title},{track.duration},{track.artist},'
                f'{track.album},{track.year},{track.position},'
                f'{track.original_artist}\n'
            )
            file.write(output_string)
