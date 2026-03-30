"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

_application = get_wsgi_application()


def application(environ, start_response):
    """
    WSGI middleware that strips FORCE_SCRIPT_NAME prefix from PATH_INFO.
    This allows Django to work behind a reverse proxy with a sub-path
    (e.g. /e-learning/e-seus/) without requiring nginx rewrite rules.
    """
    from django.conf import settings
    script_name = getattr(settings, 'FORCE_SCRIPT_NAME', None)
    if script_name:
        path_info = environ.get('PATH_INFO', '/')
        if path_info.startswith(script_name):
            environ['SCRIPT_NAME'] = script_name
            environ['PATH_INFO'] = path_info[len(script_name):] or '/'
    return _application(environ, start_response)
