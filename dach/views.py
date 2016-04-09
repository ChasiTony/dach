from __future__ import unicode_literals

import json
import logging

import requests
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt

from .utils import (
    get_access_token,
    get_and_check_capabilities,
    save_client_info
)

logger = logging.getLogger('dach')


def homepage(request):
    pass


def descriptor(request):
    if request.method == 'GET':
        return render(
            request,
            'atlassian-connect.json',
            content_type='application/json')
    raise HttpResponseNotAllowed()


@csrf_exempt
def installable(request):
    if request.method == 'POST':
        data = json.loads(smart_text(request.body))
        doc = get_and_check_capabilities(data['capabilitiesUrl'])
        client_info = {
            'oauth_id': data['oauthId'],
            'oauth_secret': data['oauthSecret'],
            'capabilities_url': data['capabilitiesUrl'],
            'capabilities_doc': doc,
            'group_id': data['groupId'],
            'room_id': data.get('roomId', None)
        }
        token = get_access_token(client_info)
        client_info['group_name'] = token.group_name

        logger.info('addon successfully installed')

# clientInfo.groupId = tokenObj.group_id;
# self.emit('installed', clientKey, clientInfo, req);
# self.emit('plugin_enabled', clientKey, clientInfo, req);
# self.settings.set('clientInfo', clientInfo, clientKey).then(function (data) {
#     self.logger.info("Saved tenant details for " + clientKey + " to database\n" + util.inspect(data));
#     self.emit('host_settings_saved', clientKey, data);
#     res.send(204);
        return HttpResponse(status=204)

def configurable(request):
    pass
