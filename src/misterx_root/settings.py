"""
Django settings for misterx_root project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


try:
    from . import local_settings
except ModuleNotFoundError:
    raise ImproperlyConfigured("Please create local_settings.py")


for i in ["ALLOWED_HOSTS", "DATABASE", "SECRET_KEY", "CSRF_TRUSTED_ORIGINS"]:
    if not hasattr(local_settings, i):
        raise ImproperlyConfigured(f"{i} is missing in local_settings.py")

SECRET_KEY = local_settings.SECRET_KEY

DEBUG = getattr(local_settings, "DEBUG", False)

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG


ALLOWED_HOSTS = local_settings.ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = local_settings.CSRF_TRUSTED_ORIGINS

INTERNAL_IPS = getattr(local_settings, "INTERNAL_IPS", ["127.0.0.1", "::1"])

SOCIAL_AUTH_OIDC_OIDC_ENDPOINT = getattr(local_settings, "SOCIAL_AUTH_OIDC_OIDC_ENDPOINT", "")
SOCIAL_AUTH_OIDC_KEY = getattr(local_settings, "SOCIAL_AUTH_OIDC_KEY", "")
SOCIAL_AUTH_OIDC_SECRET = getattr(local_settings, "SOCIAL_AUTH_OIDC_SECRET", "")
ADMIN_GROUP = getattr(local_settings, "ADMIN_GROUP", "misterx_admins")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "django_filters",
    "guardian",
    "django_tables2",
    "crispy_forms",
    "crispy_bootstrap5",
    "social_django",
    "utilities",
    "misterx",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "misterx_root.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "utilities.context_processors.read_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "misterx_root.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {"default": local_settings.DATABASE}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    "social_core.backends.open_id_connect.OpenIdConnectAuth",
    "django.contrib.auth.backends.ModelBackend",  # default
    "guardian.backends.ObjectPermissionBackend",
)
ANONYMOUS_USER_NAME = None
SOCIAL_AUTH_URL_NAMESPACE = "social"

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "utilities.auth_pipeline.oidc.assign_groups_and_attributes",
)

LOGIN_REDIRECT_URL = "/user/submit"
LOGIN_REDIRECT_URL_STAFF = "/games"

# 4 hours in seconds
SESSION_COOKIE_AGE = 4 * 60 * 60


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = getattr(local_settings, "TIME_ZONE", "UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = (BASE_DIR / "static-source",)


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap5-responsive.html"

DJANGO_TABLES2_TABLE_ATTRS = {
    "class": "table table-responsive table-striped",
    "td": {
        "class": "align-middle",
    },
    "th": {
        "_ordering": {
            "ascending": "ti ti-sort-ascending",
            "descending": "ti ti-sort-descending",
        },
    },
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

MEDIA_ROOT = getattr(local_settings, "MEDIA_ROOT", BASE_DIR / "media")

MEDIA_URL = "media/"
