from .base import *
import dj_database_url
from datetime import datetime
import os

DEBUG = False

ALLOWED_HOSTS = ['stockbridge.morphosis.org.in', '.herokuapp.com']
BASE_URL = 'stockbridge.morphosis.org.in'

START_TIME = datetime(2019, 5, 14, 19, 00, 0)
STOP_TIME = datetime(2019, 5, 15, 00, 30, 00)

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL')
    )
}

# whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# SSL/TLS settings for https security
CORS_REPLACE_HTTPS_REFERER = True
HOST_SCHEME = "https://"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 1000000
SECURE_FRAME_DENY = True
