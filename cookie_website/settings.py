"""
Django settings for cookie_website project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
from environs import Env

import django_heroku


# Environmental variables
env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = [".herokuapp.com", "localhost", "127.0.0.1"]

# Debug
INTERNAL_IPS = [
    "127.0.0.1",
]

# Twilio Information
TWILIO_ACCOUNT_SID = env.str("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env.str("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = env.str("TWILIO_NUMBER")

# Application definition

INSTALLED_APPS = [
    # Cookie Apps
    "cookie_booths.apps.CookieBoothsConfig",
    "accounts.apps.AccountsConfig",
    "pages.apps.PagesConfig",
    "troops.apps.TroopsConfig",
    # Third Party Apps
    "bootstrap4",
    "bootstrap_datepicker_plus",
    "phonenumber_field",
    # Debug Apps
    "debug_toolbar",
    # Default Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    # Debug
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # Default Middleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cookie_website.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            str(BASE_DIR.joinpath("templates")),
            str(BASE_DIR.joinpath("troops/templates")),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cookie_website.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_INPUT_FORMATS = ["%I:%M %p"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "/static/")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.CustomUser"

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# Heroku settings
django_heroku.settings(locals())

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'cfsu.cookiewebsite@gmail.com'
# EMAIL_HOST_PASSWORD = env.str("GMAIL_PASSWORD")

# Project Level Constants
GIRL_SCOUT_TROOP_LEVELS_WITH_NONE = [
    (0, "None"),
    (1, "Daisies"),
    (2, "Brownies"),
    (3, "Juniors"),
    (4, "Cadettes"),
    (5, "Seniors"),
    (6, "Ambassadors"),
]

NO_COOKIE_CAPTAIN_ID = 0
NO_DAISY_TROOP = 0
