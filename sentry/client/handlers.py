"""
sentry.client.handlers
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging
import sys
import traceback

class SentryHandler(logging.Handler):
    def emit(self, record):
        from sentry.client.models import get_client
        from sentry.client.middleware import SentryLogMiddleware

        # Fetch the request from a threadlocal variable, if available
        request = getattr(SentryLogMiddleware.thread, 'request', None)

        self.format(record)

        # Avoid typical config issues by overriding loggers behavior
        if record.name == 'sentry.errors':
            print("Recursive log message sent to SentryHandler", file=sys.stderr)
            print(record.message, file=sys.stderr)
            return

        self.format(record)
        try:
            get_client().create_from_record(record, request=request)
        except Exception:
            print("Top level Sentry exception caught - failed creating log record", file=sys.stderr)
            print(record.msg, file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            return

try:
    import logbook
except ImportError:
    pass
else:
    class SentryLogbookHandler(logbook.Handler):
        def emit(self, record):
            from sentry.client.models import get_client
            
            self.format(record)

            # Avoid typical config issues by overriding loggers behavior
            if record.name == 'sentry.errors':
                print("Recursive log message sent to SentryHandler", file=sys.stderr)
                print(record.message, file=sys.stderr)
                return

            kwargs = dict(
                message=record.message,
                level=record.level,
                logger=record.channel,
                data=record.extra,
            )
            client = get_client()
            if record.exc_info:
                return client.create_from_exception(record.exc_info, **kwargs)
            return client.create_from_text(**kwargs)

