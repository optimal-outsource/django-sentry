"""
sentry
~~~~~~

:copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

try:
    from importlib.metadata import version, PackageNotFoundError
    VERSION = version("django-sentry")
except PackageNotFoundError:
        VERSION = "unknown"
except Exception:
        VERSION = "unknown"

