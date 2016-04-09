from django.conf import settings
from django.template import Library
from django.template.defaulttags import URLNode, url
from django.utils.six.moves.urllib.parse import urljoin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import StaticNode


DACH_BASE_URL = getattr(settings, 'DACH_BASE_URL')

register = Library()


class AbsoluteURLNode(URLNode):
    def render(self, context):
        # asvar, self.asvar = self.asvar, None
        path = super(AbsoluteURLNode, self).render(context)
        abs_url = urljoin(DACH_BASE_URL, path)

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


class AbsoluteStaticFilesNode(StaticNode):

    def url(self, context):
        path = self.path.resolve(context)
        return urljoin(DACH_BASE_URL, staticfiles_storage.url(path))


@register.tag
def absstatic(parser, token):
    return AbsoluteStaticFilesNode.handle_token(parser, token)
