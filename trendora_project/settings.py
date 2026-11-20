"""
Django settings for trendora_project project.
TRENDORA – Real-Time News and Trend Intelligence
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / '.env')

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY', 'trendora-production-insecure-key-2026-sec-grade-quantum')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '*')
if allowed_hosts_env == '*':
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # TRENDORA Modular Applications
    'accounts.apps.AccountsConfig',
    'news.apps.NewsConfig',
    'trends.apps.TrendsConfig',
    'ai.apps.AiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'trendora_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trendora_project.wsgi.application'

# Database - SQLite3 as initial database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# NewsAPI & Intelligence Engine Settings
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')
DEFAULT_COUNTRY = os.getenv('DEFAULT_COUNTRY', 'us')
COLLECTION_INTERVAL_HOURS = int(os.getenv('COLLECTION_INTERVAL_HOURS', '2'))
DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', '12'))

# Groq LLM API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'qwen/qwen3.8-27b')
GROQ_TEMPERATURE = float(os.getenv('GROQ_TEMPERATURE', '0.2'))
GROQ_MAX_TOKENS = int(os.getenv('GROQ_MAX_TOKENS', '2048'))

# Sentence Transformers & FAISS Vector Store Settings
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
FAISS_STORAGE_DIR = BASE_DIR / 'data' / 'faiss'
FAISS_INDEX_PATH = FAISS_STORAGE_DIR / 'articles_index.faiss'
FAISS_METADATA_PATH = FAISS_STORAGE_DIR / 'articles_metadata.json'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
