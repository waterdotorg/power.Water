# Python system path setup
from os import path
PROJECT_ROOT = path.dirname(path.abspath(__file__))

# Django settings for project project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

############################################################################################
# Set following variables in settings_dev_private.py and/or settings_production_private.py #
############################################################################################
"""
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''

# Facebook API keys
FACEBOOK_APP_ID = ''
FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''
FACEBOOK_APP_NAMESPACE = ''

# Twitter API keys
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
"""

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = path.join(PROJECT_ROOT, "public/media/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path.join(PROJECT_ROOT, "public/static-root/")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(PROJECT_ROOT, "public/static/"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'custom.middleware.ReferrerMidddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'project.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(PROJECT_ROOT, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.humanize',
    'south',
    'easy_thumbnails',
    'gunicorn',
    'fbauth',
    'twauth',
    'custom',
    'instagallery',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'fbauth.auth.FbAuth',
    'twauth.auth.TwAuth',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    # "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    # "custom.context_processors.returning_user",
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'power',
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'facebook_status_update': {
            'level': 'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': path.join(PROJECT_ROOT, "../../logs/facebook_status_update/log.log"),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'verbose',
        },
        'twitter_status_update': {
            'level': 'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': path.join(PROJECT_ROOT, "../../logs/twitter_status_update/log.log"),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'verbose',
        },
        'facebook_og_new_friend_joined': {
            'level': 'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': path.join(PROJECT_ROOT, "../../logs/facebook_og_new_friend_joined/log.log"),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'verbose',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'custom.management.commands.facebook_status_update': {
            'handlers': ['facebook_status_update'],
            'level': 'INFO',
            'propagate': True,
        },
        'custom.management.commands.twitter_status_update': {
            'handlers': ['twitter_status_update'],
            'level': 'INFO',
            'propagate': True,
        },
        'custom.management.commands.facebook_og_new_friend_joined': {
            'handlers': ['facebook_og_new_friend_joined'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# easy_thumbnails config
THUMBNAIL_SUBDIR = 'thumbs'

# Facebook settings
FACEBOOK_PERMISSIONS_SCOPE = ['publish_actions', 'email']
FACEBOOK_LOGIN_SUCCESS_REDIRECT = '/dashboard/'
FACEBOOK_LOGIN_ERROR_REDIRECT = '/signin/'

# Twitter settings
TWITTER_LOGIN_SUCCESS_REDIRECT = '/dashboard/'
TWITTER_LOGIN_ERROR_REDIRECT = '/signin/'
TWITTER_SCREEN_NAME = 'water'

AUTH_PROFILE_MODULE = 'custom.Profile'

LOGIN_URL = '/signin/'

# Instagram Settings
INSTAGRAM_CLIENT_ID = '9d807f57a0c648db849357d3285bae86'
