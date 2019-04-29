from collections import namedtuple
import json


def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())


def json2obj(data):
    return json.loads(data.decode('utf-8'), object_hook=_json_object_hook)
