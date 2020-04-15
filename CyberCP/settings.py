"""
Django settings for CyberCP project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from six.moves.urllib.parse import (
    unquote, urlsplit, urlunsplit,
)


class DjsManifestStaticFilesStorage(ManifestStaticFilesStorage):
    manifest_strict = False

    def hashed_name(self, name, content=None, filename=None):
        # `filename` is the name of file to hash if `content` isn't given.
        # `name` is the base name to construct the new hashed filename from.
        parsed_name = urlsplit(unquote(name))
        clean_name = parsed_name.path.strip()
        if filename:
            filename = urlsplit(unquote(filename)).path.strip()
        filename = filename or clean_name
        opened = False
        if content is None:
            try:
                content = self.open(filename)
            except IOError:
                # Handle directory paths and fragments
                return name
            opened = True
        try:
            file_hash = self.file_hash(clean_name, content)
        finally:
            if opened:
                content.close()
        path, filename = os.path.split(clean_name)
        root, ext = os.path.splitext(filename)
        if file_hash is not None:
            file_hash = ".%s" % file_hash
        hashed_name = os.path.join(path, "%s%s%s" %
                                   (root, file_hash, ext))
        unparsed_name = list(parsed_name)
        unparsed_name[2] = hashed_name
        # Special casing for a @font-face hack, like url(myfont.eot?#iefix")
        # http://www.fontspring.com/blog/the-new-bulletproof-font-face-syntax
        if '?#' in name and not unparsed_name[3]:
            unparsed_name[2] += '?'
        return urlunsplit(unparsed_name)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xr%j*p!*$0d%(-(e%@-*hyoz4$f%y77coq0u)6pwmjg4)q&19f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'baseTemplate',
    'loginSystem',
    'packages',
    'websiteFunctions',
    'tuning',
    'serverStatus',
    'dns',
    'ftp',
    'userManagment',
    'databases',
    'mailServer',
    'serverLogs',
    'firewall',
    'backup',
    'managePHP',
    'manageSSL',
    'api',
    'filemanager',
    'manageServices',
    'pluginHolder',
    'emailPremium',
    'emailMarketing',
    'cloudAPI',
    'highAvailability',
    's3Backups',
    'dockerManager',
    'containerization',
    'CLManager',
    'IncBackups',
    'WebTerminal',
    'corsheaders'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'CyberCP.secMiddleware.secMiddleware'
]

ROOT_URLCONF = 'CyberCP.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'client/build')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CyberCP.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('default_db_name', 'cyberpanel'),
        'USER': os.environ.get('default_db_user', 'root'),
        'PASSWORD': os.environ.get('default_db_password', '1234'),
        'HOST': os.environ.get('default_db_host', '127.0.0.1'),
        'PORT':os.environ.get('default_db_port', '3307')
    },
    'rootdb': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('root_db_name', 'mysql'),
        'USER': os.environ.get('root_db_user', 'root'),
        'PASSWORD': os.environ.get('root_db_password', '1234'),
        'HOST': os.environ.get('root_db_host', '127.0.0.1'),
        'PORT': os.environ.get('root_db_port', '3307')
    },
}

DATABASE_ROUTERS = ['backup.backupRouter.backupRouter']

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static_root/")
REACT_APP_DIR = os.path.join(BASE_DIR, 'client')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static/"),
    os.path.join(REACT_APP_DIR, 'build', 'static'),
]

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

LANGUAGES = (
    ('en', _('English')),
    ('cn', _('Chinese')),
    ('br', _('Bulgarian')),
    ('pt', _('Portuguese')),
    ('ja', _('Japanese')),
    ('bs', _('Bosnian')),
    ('gr', _('Greek')),
    ('ru', _('Russian')),
    ('tr', _('Turkish')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('pl', _('Polish')),
    ('vi', _('Vietnamese')),
    ('it', _('Italian')),
    ('de', _('Deutsch')),
)

MEDIA_URL = '/home/cyberpanel/media/'
MEDIA_ROOT = MEDIA_URL
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800