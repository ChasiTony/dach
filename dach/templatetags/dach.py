from django.conf import settings
from django.template import Library
from django.template.defaulttags import URLNode, url
from django.utils.six.moves.urllib.parse import urljoin

register = Library()


class AbsoluteURLNode(URLNode):
    def render(self, context):
        # asvar, self.asvar = self.asvar, None
        path = super(AbsoluteURLNode, self).render(context)
        base_url = getattr(settings, 'DACH_BASE_URL', None)

        if base_url:
            abs_url = urljoin(base_url, path)
        else:
            request_obj = context['request']
            abs_url = request_obj.build_absolute_uri(path)

        if not self.asvar:
            return abs_url
        else:
            context[self.asvar] = abs_url
            return ''


@register.tag
def absurl(parser, token):
    node = url(parser, token)
    return AbsoluteURLNode(
        view_name=node.view_name,
        args=node.args,
        kwargs=node.kwargs,
        asvar=node.asvar
    )
