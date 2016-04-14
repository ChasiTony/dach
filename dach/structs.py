import json


__all__ = ['Tenant', 'Token']


class DefKeysDict(dict):
    KEYS = []

    def __init__(self, **kwargs):
        if not set(kwargs.keys()).issubset(DefKeysDict.KEYS):
            raise KeyError('invalid key/s found')
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, name, value):
        if name not in DefKeysDict.KEYS:
            raise KeyError('invalid key: %s' % name)
        super(DefKeysDict, self).__setattr__(name, value)
        super(DefKeysDict, self).__setitem__(name, value)

    __setitem__ = __setattr__

    def json(self):
        return json.dumps(self)

    @classmethod
    def from_json(cls, j):
        return cls(**json.loads(j))


class Tenant(DefKeysDict):
    DefKeysDict.KEYS.extend([
        'oauth_id',
        'group_id',
        'group_name',
        'oauth_secret',
        'room_id',
        'capabilities_url',
        'oauth_token_url',
        'api_url'
    ])


class Token(DefKeysDict):
    DefKeysDict.KEYS.extend([
        'oauth_id',
        'group_id',
        'group_name',
        'access_token',
        'expires_in',
        'scope',
        'token_type',
        'created'
    ])
