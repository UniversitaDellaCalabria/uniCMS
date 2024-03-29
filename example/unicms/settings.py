"""
Django settings for unicms project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
from . settingslocal import *

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

# SASS processor settings
# can include files not starting with "_"
SASS_PROCESSOR_INCLUDE_FILE_PATTERN = r'^.+\.scss$'
# css output compact style
SASS_OUTPUT_STYLE = 'compact'

ROOT_URLCONF = 'unicms.urls'

WSGI_APPLICATION = 'unicms.wsgi.application'

# SECURITY
X_FRAME_OPTIONS = 'SAMEORIGIN'
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
CSRF_COOKIE_HTTPONLY = True

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

# from django 3.2
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
