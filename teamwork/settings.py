"""
Django settings for teamwork project on Heroku. For more info, see:
https://github.com/heroku/heroku-django-template
For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""


import os

import dj_database_url
# Using python decouple (instead of os) for easier path management
from decouple import config
from unipath import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = Path(__file__).parent
COURSE_DIR = Path(__file__).parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY is set in .env file. See etc/example.env
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG is set in .env file. See etc/example.env
DEBUG = config('DEBUG', default=False, cast=bool)
USE_POSTGRES_LOCAL = config('USE_POSTGRES_LOCAL', default=False, cast=bool)

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    'teamwork.apps.core',
    'teamwork.apps.profiles',
    'teamwork.apps.projects',
    'teamwork.apps.courses',

    'django_adminlte',
    'django_adminlte_theme',

    #'django_extensions',

    'django.contrib.admin',

    'django_gravatar',

    'chartjs'
]

# Sets emails for notifications of error when DEBUG=False
ADMINS = config('ADMINS', default=[('Grepthink Team', 'grepthink@gmail.com')])

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')

if DEBUG:
    EMAIL_SENDGRID_KEY = os.environ.get('SENDGRID_TEST_KEY')
else:
    EMAIL_SENDGRID_KEY = os.environ.get('SENDGRID_API_KEY')

EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Grepthink Team <info@grepthink.com>'

# isProd = config('PRODUCTION', default=False)
#
# if isProd:
#     pass
#     #For Testing, comment out for production
#     #EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# else:
#     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'teamwork.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ PROJECT_DIR.child('templates'), COURSE_DIR.child('templates') ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'teamwork.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

# Setup the database manually if environment is Travis.
if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'NAME':     'travisdb',  # Must match travis.yml setting
            'USER':     'postgres',
            'PASSWORD': '',
            'HOST':     'localhost',
            'PORT':     '',
        }
    }
# Connect to postgres db described by POSTGRES_DATABASE_URL in .env file
elif USE_POSTGRES_LOCAL:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('POSTGRES_DATABASE_URL')
        )
    }
# Connect to sqlite3 db described by DATABASE_URL in .env file
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL')
        )
    }


""" Original Django Database Settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = ['teamwork.apps.core.models.EmailAddressAuthBackend', 'django.contrib.auth.backends.ModelBackend']

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = False
USE_TZ = True
DATE_FORMAT = '%Y%m%d'

# Update database configuration with $DATABASE_URL.
#db_from_env = dj_database_url.config(conn_max_age=500)
#DATABASES['default'].update(db_from_env)

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Define the static and media stuff, so Django won't have problems finding your css/js files:
STATIC_ROOT = PROJECT_DIR.parent.child('static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    PROJECT_DIR.child('static'),
)

MEDIA_ROOT = PROJECT_DIR.child('media')
MEDIA_URL = '/media/'

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

ALLOWED_SIGNUP_DOMAINS = ['*']

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Django Toolbar Uncomment to turn on

# DEBUG = True
#
# if DEBUG:
#    INTERNAL_IPS = ('127.0.0.1', 'localhost',)
#    MIDDLEWARE_CLASSES += (
#        'debug_toolbar.middleware.DebugToolbarMiddleware',
#    )
#
#    INSTALLED_APPS += (
#        'debug_toolbar',
#    )
#
#    DEBUG_TOOLBAR_PANELS = [
#        'debug_toolbar.panels.versions.VersionsPanel',
#        'debug_toolbar.panels.timer.TimerPanel',
#        'debug_toolbar.panels.settings.SettingsPanel',
#        'debug_toolbar.panels.headers.HeadersPanel',
#        'debug_toolbar.panels.request.RequestPanel',
#        'debug_toolbar.panels.sql.SQLPanel',
#        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#        'debug_toolbar.panels.templates.TemplatesPanel',
#        'debug_toolbar.panels.cache.CachePanel',
#        'debug_toolbar.panels.signals.SignalsPanel',
#        'debug_toolbar.panels.logging.LoggingPanel',
#        'debug_toolbar.panels.redirects.RedirectsPanel',
#    ]
#
#    DEBUG_TOOLBAR_CONFIG = {
#        'INTERCEPT_REDIRECTS': False,
#    }
