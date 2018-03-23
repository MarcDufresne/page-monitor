import aioredis
import click

REDIS_CONNECTION = None

EMAIL_SERVICE: str = None

MAILGUN_DOMAIN: str = None
MAILGUN_API_KEY: str = None
MAILGUN_FROM_NAME: str = None
MAILGUN_FROM_EMAIL: str = None

SMTP_HOST: str = None
SMTP_PORT: int = None
SMTP_USERNAME: str = None
SMTP_PASSWORD: str = None
SMTP_USE_TLS: bool = True
SMTP_FROM_EMAIL: str = None

redis_client = None


def set_config(raw_config: dict):
    _raw_redis = raw_config.get('redis', '127.0.0.1:6379')
    globals()['REDIS_CONNECTION'] = f'redis://{_raw_redis}'

    _raw_mailgun = raw_config.get('mailgun', {})
    globals()['MAILGUN_DOMAIN'] = _raw_mailgun.get('domain', '')
    globals()['MAILGUN_API_KEY'] = _raw_mailgun.get('api_key', '')
    globals()['MAILGUN_FROM_EMAIL'] = _raw_mailgun.get('from_email', '')
    globals()['MAILGUN_FROM_NAME'] = _raw_mailgun.get('from_name',
                                                      MAILGUN_FROM_EMAIL)

    _raw_smtp = raw_config.get('smtp', {})
    globals()['SMTP_HOST'] = _raw_smtp.get('host', 'smtp.gmail.com')
    globals()['SMTP_PORT'] = int(_raw_smtp.get('port', 587))
    globals()['SMTP_USERNAME'] = _raw_smtp.get('username', '')
    globals()['SMTP_PASSWORD'] = _raw_smtp.get('password', '')
    globals()['SMTP_USE_TLS'] = _raw_smtp.get('tls', True)
    globals()['SMTP_FROM_EMAIL'] = _raw_smtp.get('from_email',
                                                 'page-monitor@example.com')

    globals()['EMAIL_SERVICE'] = raw_config.get('email_service', 'smtp')

    if EMAIL_SERVICE == 'mailgun' and (not MAILGUN_DOMAIN or
                                       not MAILGUN_API_KEY):
        click.echo(
            click.style(
                'WARNING: Bad configuration for email action, missing either'
                'mailgun.domain or mailgun.api_key', fg='orange'))


async def init_redis():
    globals()['redis_client'] = await aioredis.create_redis(REDIS_CONNECTION)


def get_redis_client():
    return redis_client
