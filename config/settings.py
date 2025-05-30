from datetime import timedelta
from pathlib import Path

import environ
from django import __version__
from yookassa import Configuration
from yookassa.domain.common.user_agent import Version

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent

LOGS_DIR = BASE_DIR / "logs"

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "djangorestframework_camel_case",
    "corsheaders",
    "django_celery_beat",
    # local
    "config",
    "authentication",
    "lessons",
    "schedule",
    "variants",
    "user",
    "core",
    "subscriptions",
    "tasks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "djangorestframework_camel_case.middleware.CamelCaseMiddleWare",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db(),
}

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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
    "formatters": {
        "simple": {
            "format": "[{asctime}] ({levelname}) - {message}",
            "datefmt": "%d.%m.%Y %H:%M:%S",
            "style": "{",
        },
        "verbose": {
            "format": '[{asctime}] ({levelname}) "{name}:{lineno}" - {message}',
            "datefmt": "%d.%m.%Y %H:%M:%S",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "logs.log",
            "formatter": "verbose",
        },
        "django_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "django.log",
            "formatter": "simple",
        },
        "django_db": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "django_db.log",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django.request": {
            "level": "DEBUG",
            "handlers": ["console", "django_file"],
            "propagate": False,
        },
        "django.security": {
            "level": "DEBUG",
            "handlers": ["django_file"],
            "propagate": False,
        },
        "django.db": {
            "level": "DEBUG",
            "handlers": ["django_db"],
            "propagate": False,
        },
        "": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
    },
}

CACHES = {"default": env.cache()}

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "user.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "authentication.permissions.OneDevicePermission",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

PASSWORD_RESET_BASE_URL = env.str("PASSWORD_RESET_BASE_URL")
PASSWORD_RESET_TOKEN_LIFETIME = timedelta(minutes=5)

CONFIRM_MAIL_BASE_URL = env.str("CONFIRM_MAIL_BASE_URL")
CONFIRM_MAIL_TOKEN_LIFETIME = timedelta(minutes=10)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", False)
EMAIL_HOST = env.str("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND")

CELERY_BEAT_SCHEDULE = {
    "notify_subscription_overdue": {
        "task": "subscriptions.tasks.notify_subscription_overdue",
        "schedule": 60,
    }
}

PROFILE_IMAGE_COLORS = (
    {"background": "#8cf66c", "text": "#2c8112"},
    {"background": "#cc6cf6", "text": "#631281"},
    {"background": "#6c70f6", "text": "#121481"},
    {"background": "#f66c6c", "text": "#811212"},
    {"background": "#f66cee", "text": "#81126d"},
    {"background": "#f2f66c", "text": "#afb40c"},
    {"background": "#68eee5", "text": "#108e85"},
    {"background": "#68eebf", "text": "#11815a"},
    {"background": "#f5aa65", "text": "#814711"},
    {"background": "#bcf565", "text": "#538010"},
)

KINESCOPE = {
    "API_TOKEN": env.str("KINESCOPE_API_KEY"),
    "API_BASE": "https://api.kinescope.io",
    "PROJECT_ID": "e307165d-6a96-4f6f-b692-1a26b4e93d9c",
    "STREAM": {
        "type": "auto-webinar",
        "video_presets": ["360p", "480p", "720p", "1080p", "1440p"],
    },
}

Configuration.configure_user_agent(framework=Version("Django", __version__))
Configuration.account_id = env.int("YOOKASSA_ACCOUNT_ID")
Configuration.secret_key = env.str("YOOKASSA_SECRET_KEY")
