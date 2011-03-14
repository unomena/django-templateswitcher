from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.core.xheaders import populate_xheaders
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.views.generic.simple import direct_to_template

from models import Page

DEFAULT_TEMPLATE = 'flatpages/default.html'

# This view is called from FlatpageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
@csrf_protect
def flatpageview(request, template=None):
    """
    A modified copy of flatpage view
    Supports mobile template switcher and fallback to direct_to_template
    """
    url = request.path_info
    # append trailing slash
    if not url.endswith('/') and settings.APPEND_SLASH:
        return HttpResponseRedirect("%s/" % request.path)
    if not url.startswith('/'):
        url = "/" + url

    # switch template mode
    if not hasattr(request, 'template_set'):
        raise Exception('Developer Error! Request does not contain template_set')

    page = False
    try:
        page = get_object_or_404(Page, url__exact=url,
            template_set__exact=request.template_set
        )
    except:
        try:
            page = get_object_or_404(Page, url__exact=url,
                template_set__in=['',None]
            )
        except:
            if template:
                return direct_to_template(request, template=template)

    if not page:
        raise Http404

    template = page.template
    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    page.title = mark_safe(page.title)
    page.content = mark_safe(page.content)


    t = loader.select_template((template, DEFAULT_TEMPLATE))
    c = RequestContext(request, {
        'page': page,
    })
    response = HttpResponse(t.render(c))

    if page:
        populate_xheaders(request, response, Page, page.id)

    return response


