import json
import uuid


class JSONDecoder(json.JSONDecoder):
    pass


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return obj.urn
        return json.JSONEncoder.default(self, obj)
