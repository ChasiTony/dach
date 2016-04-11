import logging

from functools import wraps
from django.http import HttpResponse
from django.utils.decorators import available_attrs

logger = logging.getLogger('dach')


def tenant_passes_test(test_func):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            return HttpResponse('JWT token required', status=401)
        return _wrapped_view
    return decorator


def tenant_required(function=None):
    actual_decorator = tenant_passes_test(
        lambda request: hasattr(request, 'tenant')
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
