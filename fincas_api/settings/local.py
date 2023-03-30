from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bdfincas_api',
        'USER': 'root',
        'PASSWORD': 'd1n4m1kjr',  # get_env_setting('DB_MYSQL_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
    }
    
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
#STATIC_ROOT = 'static/'
