import os

import neomodel

from autodjbackend.models import Track, SameTrackNumber


if __name__ == '__main__':
    bolt_url = os.environ.get(
        'NEO4J_BOLT_URL', 'bolt://neo4j:password@db:7687'
    )

    print('Connecting to db')
    neomodel.db.set_connection(bolt_url)

    print('Track numbers.')
    print('Getting buckets')
    get_track_keys_query = 'MATCH (n:Track) RETURN DISTINCT(n.position)'

    results, _ = neomodel.db.cypher_query(get_track_keys_query)

    track_numbers = [number[0] for number in results]

    del results

    for number in track_numbers:
        print(f'Getting tracks with number {number}')
        get_tracks_query = f'MATCH (n:Track {{position:{number}}}) RETURN n'

        results, _ = neomodel.db.cypher_query(get_tracks_query)
        tracks = [Track.inflate(row[0]) for row in results]

        del results

        print('Tracks fetched.')

        link_node = SameTrackNumber(track_number=number)
        link_node.save()

        print('Link node saved')

        for track in tracks:
            track.same_track_number.connect(link_node)

        print(f'Finished bucket {number}')
