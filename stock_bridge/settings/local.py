from .base import *
from datetime import datetime

DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', 'localhost']
BASE_URL = '192.168.91.133:8000'

START_TIME = datetime(2019, 4, 12, 4, 00, 0)
STOP_TIME = datetime(2020, 5, 5, 2, 00, 0)

# removing SSL/TLS settings for local environment
CORS_REPLACE_HTTPS_REFERER = False
HOST_SCHEME = "http://"
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = None
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_FRAME_DENY = False
