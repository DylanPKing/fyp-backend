from neomodel import (
    IntegerProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty
)


class KeywordInTitle(StructuredNode):

    uuid = UniqueIdProperty()
    keyword = StringProperty(required=True)

    keyword_in_title = RelationshipTo('Track', 'KEYWORD_IN_TITLE')


class SameOriginalArtist(StructuredNode):

    uuid = UniqueIdProperty()
    original_artist = StringProperty(required=True)

    same_original_artist = RelationshipTo('Track', 'SAME_ORIGINAL_ARTIST')


class SameTrackNumber(StructuredNode):

    uuid = UniqueIdProperty()
    track_number = IntegerProperty(required=True)

    same_track_number = RelationshipTo('Track', 'SAME_NUMBER')


class SameYear(StructuredNode):

    uuid = UniqueIdProperty()
    year = IntegerProperty(required=True)

    same_year = RelationshipTo('Track', 'SAME_YEAR')


class Track(StructuredNode):

    # Attributes
    uuid = UniqueIdProperty()
    title = StringProperty(required=True)
    artist = StringProperty(required=True)
    album = StringProperty(required=True)
    year = IntegerProperty(default=0)
    position = IntegerProperty(default=0)
    duration = IntegerProperty(default=0)
    original_artist = StringProperty()

    same_original_artist = RelationshipTo(
        'SameOriginalArtist', 'SAME_ORIGINAL_ARTIST'
    )
    keyword_in_title = RelationshipTo('KeywordInTitle', 'KEYWORD_IN_TITLE')
    same_track_number = RelationshipTo('SameTrackNumber', 'SAME_NUMBER')
    same_year = RelationshipTo('SameYear', 'SAME_YEAR')

    @property
    def serialize(self):
        return {
            'uuid': self.uuid,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'year': self.year,
            'position': self.position,
            'duration': self.duration,
            'original_artist': self.original_artist,
        }
