"""
sentry.web.urls
~~~~~~~~~~~~~~~

:copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django.urls import path, re_path
from django.views.defaults import page_not_found

from sentry.web import views, feeds


def handler404(request, exception, template_name='sentry/404.html'):
        return page_not_found(request, exception, template_name=template_name)


def handler500(request):
    """
    500 error handler.

    Templates: `500.html`
    Context: None
    """
    from django.template import Context, loader
    from django.http import HttpResponseServerError

    context = {'request': request}

    t = loader.get_template('sentry/500.html')
    return HttpResponseServerError(t.render(Context(context)))


urlpatterns = [
    re_path(r'_static/(?P<path>.*)', views.static_media, name='sentry-media'),

    # Feeds

    path('feeds/messages.xml', feeds.MessageFeed(), name='sentry-feed-messages'),
    path('feeds/summaries.xml', feeds.SummaryFeed(), name='sentry-feed-summaries'),

    # JS and API

    path('jsapi/', views.ajax_handler, name='sentry-ajax'),
    path('store/', views.store, name='sentry-store'),

    # Normal views

    path('login', views.login, name='sentry-login'),
    path('logout', views.logout, name='sentry-logout'),
    re_path(r'group/(\d+)', views.group, name='sentry-group'),
    re_path(r'group/(\d+)/messages', views.group_message_list, name='sentry-group-messages'),
    re_path(r'group/(\d+)/messages/(\d+)', views.group_message_details, name='sentry-group-message'),
    re_path(r'group/(\d+)/actions/([\w_-]+)', views.group_plugin_action, name='sentry-group-plugin-action'),

    path('search', views.search, name='sentry-search'),

    path('', views.index, name='sentry'),
]
