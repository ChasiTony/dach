import logging

import requests

from dach.connect.auth import get_access_token
from dach.utils import lookup_dict

logger = logging.getLogger('dach')


def _get_all(tenant, url):
    token = get_access_token(tenant)
    objects = []
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(token.access_token)
    }
    while url:
        res = requests.get(url, headers=headers)
        if res.status_code != requests.codes.ok:
            return res.status_code, objects, res.text
        hooks = res.json()
        url = lookup_dict(hooks, 'links.next', strict=False)
        objects.extend(lookup_dict(hooks, 'items'))
    return res.status_code, objects, res.text


def get_all_rooms(tenant):
    url = '{}/room'.format(tenant.api_url)
    return _get_all(tenant, url)


def get_all_members(tenant, room_id):
    url = '{}/room/{}/member'.format(tenant.api_url, room_id)
    return _get_all(tenant, url)


def get_all_participants(tenant, room_id):
    url = '{}/room/{}/participant'.format(tenant.api_url, room_id)
    return _get_all(tenant, url)


def get_all_webhooks(tenant, room_id):
    url = '{}/room/{}/webhook'.format(tenant.api_url, room_id)
    return _get_all(tenant, url)
