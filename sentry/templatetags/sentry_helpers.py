from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from sentry.plugins import GroupActionProvider
from sentry.utils import json
from templatetag_sugar.register import tag
from templatetag_sugar.parser import Name, Variable, Constant, Optional

import datetime

register = template.Library()

@register.filter
def pprint(value, break_after=10):
    """A wrapper around pprint.pprint -- for debugging, really."""
    from pprint import pformat

    value = pformat(value)

    return '\u200B'.join([value[i:i+break_after] for i in range(0, len(value), break_after)])

# seriously Django?
@register.filter
def plus(value, amount):
    return int(value) + int(amount)

@register.filter
def has_charts(group):
    from sentry.utils.charts import has_charts
    if hasattr(group, '_state'):
        db = group._state.db
    else:
        db = 'default'
    return has_charts(db)

@register.filter
def as_sorted(value):
    return sorted(value)

@register.filter
def is_dict(value):
    return isinstance(value, dict)

@register.filter
def small_count(v):
    z = [
        (1000000000, _('b')),
        (1000000, _('m')),
        (1000, _('k')),
    ]
    v = int(v)
    for x, y in z:
        o, p = divmod(v, x)
        if o:
            if len(str(o)) > 2 or not p:
                return '%d%s' % (o, y)
            return '%.1f%s' % (v / float(x), y)
    return v

@register.filter
def with_priority(result_list, key='score'):
    if result_list:
        if isinstance(result_list[0], (dict, list, tuple)):
            _get = lambda x, k: x[k]
        else:
            _get = lambda x, k: getattr(x, k)

        min_, max_ = min([_get(r, key) for r in result_list]), max([_get(r, key) for r in result_list])
        mid = (max_ - min_) / 4
        for result in result_list:
            val = _get(result, key)
            if val > max_ - mid:
                priority = 'veryhigh'
            elif val > max_ - mid * 2:
                priority = 'high'
            elif val > max_ - mid * 3:
                priority = 'medium'
            elif val > max_ - mid * 4:
                priority = 'low'
            else:
                priority = 'verylow'
            yield result, priority

@register.filter
def num_digits(value):
    return len(str(value))

@register.filter
def to_json(data):
    return json.dumps(data)

@register.simple_tag
def sentry_version():
    import sentry
    return sentry.VERSION

@register.filter
def get_actions(group, request):
    action_list = []
    for cls in GroupActionProvider.plugins.values():
        inst = cls(group.pk)
        action_list = inst.actions(request, action_list, group)
    for action in action_list:
        yield action[0], action[1], request.path == action[1]

@register.filter
def get_panels(group, request):
    panel_list = []
    for cls in GroupActionProvider.plugins.values():
        inst = cls(group.pk)
        panel_list = inst.panels(request, panel_list, group)
    for panel in panel_list:
        yield panel[0], panel[1], request.path == panel[1]

@register.filter
def get_widgets(group, request):
    for cls in GroupActionProvider.plugins.values():
        inst = cls(group.pk)
        resp = inst.widget(request, group)
        if resp:
            yield resp

@register.filter
def get_tags(group, request):
    tag_list = []
    for cls in GroupActionProvider.plugins.values():
        inst = cls(group.pk)
        tag_list = inst.tags(request, tag_list, group)
    for tag in tag_list:
        yield tag

@register.filter
def timesince(value):
    from django.template.defaultfilters import timesince
    if not value:
        return _('Never')
    if value < datetime.datetime.now() - datetime.timedelta(days=5):
        return value.date()
    value = (' '.join(timesince(value).split(' ')[0:2])).strip(',')
    if value == _('0 minutes'):
        return _('Just now')
    if value == _('1 day'):
        return _('Yesterday')
    return value + _(' ago')

@register.filter(name='truncatechars')
@stringfilter
def truncatechars(value, arg):
    """
    Truncates a string after a certain number of chars.

    Argument: Number of chars to truncate after.
    """
    try:
        length = int(arg)
    except ValueError: # Invalid literal for int().
        return value # Fail silently.
    if len(value) > length:
        return value[:length] + '...'
    return value
truncatechars.is_safe = True

def paginate(context, queryset_or_list, request, asvar=None, per_page=25, is_endless=True):
    """
    Replacement for django-pagination's paginate helper.
    
    Usage in templates:
        {% paginate queryset_or_list from request as foo %}
    
    Returns a dict:
        {
            'objects': page_obj.object_list,
            'paging': rendered HTML for pager
        }
    """
    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset_or_list, per_page)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        # For endless pagination, optionally return the last page
        page_obj = paginator.page(paginator.num_pages)

    # Prepare the context for the pager template
    paging_context = {
        'paginator': paginator,
        'page_obj': page_obj,
        'is_endless': is_endless,
        'request': request,
    }

    # Render the pager HTML (you can reuse your old template)
    paging = mark_safe(render_to_string('sentry/partial/_pager.html', paging_context, request=request))

    result = {
        'objects': page_obj.object_list,
        'paging': paging,
    }

    if asvar:
        context[asvar] = result
        return ''

    return result

