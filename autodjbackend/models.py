from neomodel import (
    IntegerProperty,
    Relationship,
    StringProperty,
    StructuredNode,
    UniqueIdProperty
)


class KeywordInTitle(StructuredNode):

    uuid = UniqueIdProperty()
    keyword = StringProperty(required=True)


class SameOriginalArtist(StructuredNode):

    uuid = UniqueIdProperty()
    original_artist = StringProperty(required=True)


class SameTrackNumber(StructuredNode):

    uuid = UniqueIdProperty()
    track_number = IntegerProperty(required=True)


class SameYear(StructuredNode):

    uuid = UniqueIdProperty()
    year = IntegerProperty(required=True)


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

    # Undirected Relationships
    same_original_artist = Relationship(
        'SameOriginalArtist', 'SAME_ORIGINAL_ARTIST'
    )
    keyword_in_title = Relationship('KeywordInTitle', 'KEYWORD_IN_TITLE')
    same_track_number = Relationship('SameTrackNumber', 'SAME_NUMBER')
    same_year = Relationship('SameYear', 'SAME_YEAR')

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
