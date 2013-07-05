PROJECT = 'stargazer'

LOCALE = 'en_US'

PROCESSES = 1

PORT = 8000

DEBUG = True

LOGGING = {
    'level': 'INFO',
    'propagate': 1,
    'color': True,
}

LOG_REQUEST = True

LOG_RESPONSE = False

TIME_ZONE = 'Asia/Shanghai'

STATIC_PATH = 'static'

TEMPLATE_PATH = 'template'

LOGGING_IGNORE_URLS = [
    '/favicon.ico',
]

GITHUB_CLIENT_ID = '2558ef592a5918519c0b'

GITHUB_CLIENT_SECRET = '91d985197e979af340aaddabf9a5cb6b325fe0b7'

GITHUB_REDIRECT_URI = 'http://127.0.0.1:8000/oauth'
