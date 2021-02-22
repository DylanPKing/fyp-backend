import os

import neomodel

from autodjbackend.models import Track, SameYear


if __name__ == '__main__':
    bolt_url = os.environ.get(
        'NEO4J_BOLT_URL', 'bolt://neo4j:password@db:7687'
    )

    print('Connecting to db')
    neomodel.db.set_connection(bolt_url)

    print('Track numbers.')
    print('Getting buckets')
    get_track_keys_query = 'MATCH (n:Track) RETURN DISTINCT(n.year)'

    results, _ = neomodel.db.cypher_query(get_track_keys_query)

    track_years = [number[0] for number in results]

    del results

    for year in track_years:
        print(f'Getting tracks with year {year}')
        get_tracks_query = f'MATCH (n:Track {{year:{year}}}) RETURN n'

        results, _ = neomodel.db.cypher_query(get_tracks_query)
        tracks = [Track.inflate(row[0]) for row in results]

        del results

        print('Tracks fetched.')

        link_node = SameYear(year=year)
        link_node.save()

        print('Link node saved')

        print('Starting linking now.')
        for track in tracks:
            track.same_year.connect(link_node)
            link_node.same_year.connect(track)

        print(f'Finished bucket {year}')
