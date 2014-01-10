from .common import *

import os


DEBUG = False
TEMPLATE_DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['GSC_LOCK_SECRET_KEY']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

ROOT_URLCONF = 'gsc_lock.urls.production'
