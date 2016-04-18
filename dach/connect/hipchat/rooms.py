import logging

import requests

from dach.connect.auth import get_access_token
from dach.utils import lookup_dict

logger = logging.getLogger(__name__)


def _get_all(tenant, url):
    token = get_access_token(tenant)
    objects = []
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(token.access_token)
    }
    while url:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return False, objects, res
        hooks = res.json()
        url = lookup_dict(hooks, 'links.next', strict=False)
        objects.extend(lookup_dict(hooks, 'items'))
    return True, objects, res


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


def update_addon_ui(tenant, room_id, glance):
    url = '{}/addon/ui/room/{}'.format(tenant.api_url, room_id)
    token = get_access_token(tenant)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(token.access_token)
    }
    res = requests.post(url, headers=headers, json={'glance': [ glance ]})
    return res.status_code == 204, None, res


