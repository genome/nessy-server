from .common import *

import os


DEBUG = True
TEMPLATE_DEBUG = True

SECRET_KEY = 'testing*secret*key'


INSTALLED_APPS += [
    'django.contrib.admin',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:1",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level':'INFO',
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

ROOT_URLCONF = 'gsc_lock.urls.development'
