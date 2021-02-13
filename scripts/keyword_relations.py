import os

import neomodel

from autodjbackend.models import Track, KeywordInTitle


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


if __name__ == '__main__':
    bolt_url = os.environ.get(
        'NEO4J_BOLT_URL', 'bolt://neo4j:password@db:7687'
    )

    print('Connecting to db')
    neomodel.db.set_connection(bolt_url)

    for keyword in KEYWORDS:
        print(f'Getting tracks with keyword {keyword}')
        get_tracks_query = (
            'MATCH (n:Track) WHERE toLower(n.title) CONTAINS $keyword RETURN n'
        )
        params = {'keyword': keyword}

        results, _ = neomodel.db.cypher_query(get_tracks_query, params=params)
        tracks = [Track.inflate(row[0]) for row in results]

        del results

        print(f'Tracks fetched: {len(tracks)}')

        link_node = KeywordInTitle(keyword=keyword)
        link_node.save()

        print('Link node saved')

        print('Starting linking now')
        for track in tracks:
            track.keyword_in_title.connect(link_node)

        print(f'Completed bucket {keyword}')
