from neomodel import (
    IntegerProperty,
    Relationship,
    StringProperty,
    StructuredNode,
    UniqueIdProperty
)


class Track(StructuredNode):

    # Attributes
    uuid = UniqueIdProperty()
    title = StringProperty(required=True)
    artist = StringProperty(required=True)
    album = StringProperty(required=True)
    year = IntegerProperty(default=0)
    position = IntegerProperty(default=0)
    original_artist = StringProperty()

    # Undirected Relationships
    same_artist = Relationship('Track', 'SAME_ARTIST')
    keyword_in_title = Relationship('Track', 'KEYWORD_IN_TITLE')
    same_number = Relationship('Track', 'SAME_NUMBER')
    same_year = Relationship('Track', 'SAME_YEAR')
    cover = Relationship('Track', 'COVER')
