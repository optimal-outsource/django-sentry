"""
sentry.plugins.sentry_redmine.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django import forms
from django.core.context_processors import csrf
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.urls import reverse
from django.utils.safestring import mark_safe

from sentry.models import GroupedMessage
from sentry.plugins import GroupActionProvider
from sentry.plugins.sentry_redmine import conf
from sentry.utils import json

import base64
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse

class RedmineIssue(models.Model):
    group = models.ForeignKey(GroupedMessage)
    issue_id = models.PositiveIntegerField()

class RedmineIssueForm(forms.Form):
    subject = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea())

class CreateRedmineIssue(GroupActionProvider):
    title = 'Create Redmine Issue'

    def actions(self, request, action_list, group):
        if 'redmine' not in group.data:
            action_list.append((self.title, self.__class__.get_url(group.pk)))
        return action_list

    def view(self, request, group):
        if request.POST:
            form = RedmineIssueForm(request.POST)
            if form.is_valid():
                data = json.dumps({
                    'key': conf.REDMINE_API_KEY,
                    'issue': {
                        'subject': form.cleaned_data['subject'],
                        'description': form.cleaned_data['description'],
                    }
                })
                url = conf.REDMINE_URL + '/projects/' + conf.REDMINE_PROJECT_SLUG + '/issues.json'
                
                req = urllib.request.Request(url, urllib.parse.urlencode({
                    'key': conf.REDMINE_API_KEY,
                }), headers={
                    'Content-type': 'application/json',
                })

                if conf.REDMINE_USERNAME and conf.REDMINE_PASSWORD:
                    authstring = base64.encodestring('%s:%s' % (conf.REDMINE_USERNAME, conf.REDMINE_PASSWORD))[:-1]
                    req.add_header("Authorization", "Basic %s" % authstring)
                
                try:
                    response = urllib.request.urlopen(req, data).read()
                except urllib.error.HTTPError as e:
                    if e.code == 422:
                        data = json.loads(e.read())
                        form.errors['__all__'] = 'Missing or invalid data'
                        for message in data:
                            for k, v in message.items():
                                if k in form.fields:
                                    form.errors.setdefault(k, []).append(v)
                                else:
                                    form.errors['__all__'] += '; %s: %s' % (k, v)
                    else:
                        form.errors['__all__'] = 'Bad response from Redmine: %s %s' % (e.code, e.msg)
                except urllib.error.URLError as e:
                    form.errors['__all__'] = 'Unable to reach Redmine host: %s' % (e.reason,)
                else:
                    data = json.loads(response)
                    RedmineIssue.objects.create(group=group, issue_id=data['issue']['id'])
                    group.data['redmine'] = {'issue_id': data['issue']['id']}
                    group.save()
                    return HttpResponseRedirect(reverse('sentry-group', args=[group.pk]))
        else:
            description = 'Sentry Message: %s' % request.build_absolute_uri(group.get_absolute_url())
            description += '\n\n<pre>' + (group.traceback or group.message) + '</pre>'

            form = RedmineIssueForm(initial={
                'subject': group.error(),
                'description': description,
            })
            
        global_errors = form.errors.get('__all__')

        BASE_TEMPLATE = "sentry/group/details.html"

        context = locals()
        context.update(csrf(request))

        return render_to_response('sentry/plugins/redmine/create_issue.html', context)

    def tags(self, request, tags, group):
        if 'redmine' in group.data:
            issue_id = group.data['redmine']['issue_id']
            tags.append(mark_safe('<a href="%s">#%s</a>' % (
                '%s/issues/%s' % (conf.REDMINE_URL, issue_id),
                issue_id,
            )))
        return tags
