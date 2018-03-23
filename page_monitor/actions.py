import logging
from abc import ABCMeta

import aiohttp
import jinja2
import sender
from jinja2 import PackageLoader

from page_monitor import config

env = jinja2.Environment(loader=PackageLoader('page_monitor', 'templates'))
email_template = env.get_template('email.html')
logger = logging.getLogger(__name__)


class Action(metaclass=ABCMeta):
    ACTION_TYPE = ''


class ActionEmail(Action):
    ACTION_TYPE = 'email'

    def __init__(self, email_to: str):
        self.email_to = email_to

    async def send_email(self, url: str, name: str, diff: str):
        lines = []
        for line in diff.split('\n'):
            if line.startswith('+ '):
                line = f'<span style="color: #28a745">{line}</span>'
            elif line.startswith('- '):
                line = f'<span style="color: #dc3545">{line}</span>'
            lines.append(line)
        colored_diff = '<br>'.join(lines)

        rendered_template = email_template.render(name=name, url=url,
                                                  colored_diff=colored_diff)

        text_content = f'''
        Content change detected for {name}

        {diff}

        See here: {url}
        '''

        subject = f'Content change detected for {name}'

        if config.EMAIL_SERVICE == 'smtp':
            await self._send_with_smtp(subject, text_content,
                                       rendered_template)
        elif config.EMAIL_SERVICE == 'mailgun':
            await self._send_with_mailgun(subject, text_content,
                                          rendered_template)

    async def _send_with_smtp(self, subject: str, text_content: str,
                              html_content: str):
        message = sender.Message(subject)
        message.html = html_content
        message.body = text_content
        message.to = self.email_to
        message.fromaddr = f'{config.SMTP_FROM_EMAIL}'

        mail = sender.Mail(host=config.SMTP_HOST,
                           username=config.SMTP_USERNAME,
                           password=config.SMTP_PASSWORD,
                           port=config.SMTP_PORT, use_tls=config.SMTP_USE_TLS)

        mail.send(message)

    async def _send_with_mailgun(self, subject: str, text_content: str,
                                 html_content: str):
        mailgun_url = (f'https://api.mailgun.net/v3/'
                       f'{config.MAILGUN_DOMAIN}/messages')

        mailgun_data = {
            'from': f'{config.MAILGUN_FROM_NAME} '
                    f'<{config.MAILGUN_FROM_EMAIL}>',
            'to': [self.email_to],
            'subject': subject,
            'text': text_content,
            'html': html_content
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(mailgun_url, auth=aiohttp.BasicAuth(
                    "api", config.MAILGUN_API_KEY), data=mailgun_data) as r:
                try:
                    r.raise_for_status()
                    logger.info(f"Sent email to {self.email_to}")
                except Exception:
                    logger.exception(f'Failed to send email to '
                                     f'{self.email_to}')


class ActionTelegram(Action):
    ACTION_TYPE = 'telegram'

    def __init__(self, chat_id: str):
        self.chat_id = chat_id

    def send_telegram_message(self, url: str, content: str = None):
        print(f"Would send telegram message to {self.chat_id} for "
              f"url {url}")
