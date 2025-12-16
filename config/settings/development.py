"""
Configuración de desarrollo
"""
from .base import *

DEBUG = True

# Hosts permitidos en desarrollo
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Apps adicionales para desarrollo
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# Middleware adicional para desarrollo
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Configuración de Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Email backend para desarrollo (imprime en consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging más detallado en desarrollo
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# CORS más permisivo en desarrollo
CORS_ALLOW_ALL_ORIGINS = True

# Deshabilitar seguridad de cookies en desarrollo
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
