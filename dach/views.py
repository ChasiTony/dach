from __future__ import unicode_literals

import json
import logging

from django.db import transaction
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt

from .connect import (get_descriptor, create_tenant, get_access_token,
                      get_and_check_capabilities)
from .utils import dotdict

# DESCRIPTOR = dotdict(json.loads(get_template(
#     getattr(
#         settings,
#         'DACH_TEMPLATE_NAME',
#         'atlassian-connect.json')
#     ).render()))


logger = logging.getLogger('dach')


def homepage(request):
    pass


def descriptor(request):
    if request.method == 'GET':
        return HttpResponse(
            json.dumps(get_descriptor()),
            content_type='application/json'
        )
    return HttpResponseNotAllowed()


@csrf_exempt
def installable(request):
    if request.method == 'POST':
        info = dotdict(json.loads(smart_text(request.body)))
        doc = get_and_check_capabilities(info.capabilitiesUrl)
        tenant = create_tenant(info, doc)
        token = get_access_token(tenant)
        tenant.group_name = token.group_name
        tenant.save()
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


@csrf_exempt
def uninstall(request, oauth_id):
    if request.method == 'DELETE':
        print('uninstall', oauth_id)
