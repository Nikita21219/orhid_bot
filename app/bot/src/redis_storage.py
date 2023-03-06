import redis
import json
from config import *

class RedisStorage:
    def __init__(self):
        self._client = redis.Redis(host=REDIS_HOST)

    def connected(self):
        try:
            self._client.ping()
            return True
        except redis.ConnectionError:
            return False

    def load_data(self, key_name: str):
        data = self._client.get(key_name)
        try:
            json_data = json.loads(data)
        except TypeError:
            return None
        return json_data

    def dump_data(self, data, key_name: str):
        json_str = json.dumps(data)
        self._client.set(key_name, json_str)

    def set(self, key: str, val: str):
        self._client.set(key, val)

    def get(self, key: str):
        return self._client.get(key)
