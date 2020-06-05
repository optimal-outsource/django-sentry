"""
sentry.client.models
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""



import sys
import logging
import warnings

from django.core.signals import got_request_exception

from sentry.conf import settings

logger = logging.getLogger('sentry.errors')

if settings.SERVERS:
    class MockTransaction(object):
        pass

    transaction = MockTransaction()
else:
    from django.db import transaction

_client = (None, None)


def get_client():
    global _client
    if _client[0] != settings.CLIENT:
        module, class_name = settings.CLIENT.rsplit('.', 1)
        _client = (settings.CLIENT, getattr(__import__(module, {}, {}, class_name), class_name)())
    return _client[1]


client = get_client()


@transaction.atomic
def sentry_exception_handler(request=None, **kwargs):
    exc_info = sys.exc_info()
    try:

        if settings.DEBUG or getattr(exc_info[0], 'skip_sentry', False):
            return

        extra = dict(
            request=request,
        )

        message_id = get_client().create_from_exception(**extra)
    except Exception as exc:
        try:
            logger.exception('Unable to process log entry: %s' % (exc,))
        except Exception as exc:
            warnings.warn('Unable to process log entry: %s' % (exc,))
    finally:
        del exc_info


got_request_exception.connect(sentry_exception_handler)

