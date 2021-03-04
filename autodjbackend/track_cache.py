import time


class TrackCache:
    _instance = None

    def __init__(self):
        self.link_node_cache = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TrackCache()

        return cls._instance

    def get_tracks_from_link_node(self, uuid):
        cache = self.link_node_cache[uuid]

        now = time.time()
        if now - cache['time'] > 3600:
            del self.link_node_cache[uuid]
            raise KeyError

        return cache['tracks']

    def add_result_to_cache(self, uuid, result):
        self.link_node_cache[uuid] = {
            'tracks': result,
            'time': time.time()
        }
