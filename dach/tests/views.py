from django.http import HttpResponse
from dach.decorators import tenant_required


@tenant_required
def jwt_test_view(request):
    return HttpResponse(status=204)
