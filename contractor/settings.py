# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@(a3yjcc-d3uxt)q7n(tvdfhe4$%u2(dvkd9^cg26+4wmih7l7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# PXE host settings

CONTRACTOR_HOST = 'http://contractor/'
PXE_IMAGE_LOCATION = 'http://static/pxe/'

# set to None to disable
DEBUG_DUMP_LOCATION = '/tmp'

# get plugins
import os
from contractor import plugins

plugin_list = []
plugin_dir = os.path.dirname( plugins.__file__ )
for item in os.scandir( plugin_dir ):
  if not item.is_dir() or not os.path.exists( os.path.join( plugin_dir, item.name, 'models.py' ) ):
    continue

  plugin_list.append( 'contractor.plugins.{0}'.format( item.name ) )

# Application definition
INSTALLED_APPS = (
    'contractor.User',
    'contractor.Directory',
    'contractor.Site',
    'contractor.BluePrint',
    'contractor.Utilities',
    'contractor.Building',
    'contractor.Foreman',
    'contractor.SubContractor',
    'contractor.PostOffice',
    *plugin_list,
    'other_plugins.text_file',
    'other_plugins.status_indicator',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'contractor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'contractor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/contractor/db.sqlite3',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

BIND_ALLOW_TRANSFER = []
BIND_SOA_EMAIL = 'hostmaster.site1.local'
BIND_NS_LIST = [ 'eth0.contractor.site1.local' ]
