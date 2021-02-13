import os

import neomodel

from autodjbackend.models import Track, SameOriginalArtist


if __name__ == '__main__':
    bolt_url = os.environ.get(
        'NEO4J_BOLT_URL', 'bolt://neo4j:password@db:7687'
    )

    print('Connecting to db')
    neomodel.db.set_connection(bolt_url)

    print('Track numbers.')
    print('Getting buckets')
    get_track_keys_query = 'MATCH (n:Track) RETURN DISTINCT(n.original_artist)'

    results, _ = neomodel.db.cypher_query(get_track_keys_query)

    original_artists = [number[0] for number in results]

    del results

    for original_artist in original_artists:
        print(f'Getting tracks with original artist {original_artist}')
        get_tracks_query = 'MATCH (n:Track {original_artist:$artist}) RETURN n'

        results, _ = neomodel.db.cypher_query(
            get_tracks_query, {'artist': original_artist}
        )
        tracks = [Track.inflate(row[0]) for row in results]

        del results

        print('Tracks fetched.')

        link_node = SameOriginalArtist(original_artist=original_artist)
        link_node.save()

        print('Link node saved')

        print('Starting linking now.')
        for track in tracks:
            track.same_original_artist.connect(link_node)

        print(f'Finished bucket {original_artist}')
