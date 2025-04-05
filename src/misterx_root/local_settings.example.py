from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# Replace with a random string, e.g. sourced with
# `head -c 500 /dev/random | tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' | fold -w 50 | head -n 1`
SECRET_KEY = ""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "::1"]

# The production domains shouldn't use http but https
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1", "http://::1"]

# sqlite database, not suitable for production, useful for development
# DATABASE = {
#     "ENGINE": "django.db.backends.sqlite3",
#     "NAME": BASE_DIR / "db.sqlite3",
#     "OPTIONS": {
#         "transaction_mode": "EXCLUSIVE"
#     },
# }

# postgresql database, recommended for production
DATABASE = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "misterx",
    "USER": "misterx",
    "PASSWORD": "SECUREPASSWORD",
    "HOST": "localhost",
    "CONN_MAX_AGE": 300,
}

TIME_ZONE = "UTC"

SOCIAL_AUTH_OIDC_OIDC_ENDPOINT = None
SOCIAL_AUTH_OIDC_KEY = None
SOCIAL_AUTH_OIDC_SECRET = None

# EMAIL_CONFIG = {
#     "host": "",
#     "user": "",
#     "password": "",
#     "from_email": "",
# }
