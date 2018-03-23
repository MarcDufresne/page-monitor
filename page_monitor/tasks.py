import difflib
import hashlib
import logging
import re
from typing import List, Tuple

import time

from page_monitor.actions import Action, ActionEmail, ActionTelegram
from page_monitor.conditions import CONDITION, CONDITION_TYPE, Condition
from page_monitor.config import get_redis_client
from page_monitor.content import get_content

logger = logging.getLogger(__name__)


class Task:
    def __init__(self, url: str, css_selector: str, interval: int,
                 actions: List[Action], conditions: List[Condition] = None,
                 condition_logic: str = None, first_only: bool = False,
                 render: bool = False, name: str = None):
        self.url = url
        self.name = name or url
        self.css_selector = css_selector
        self.first_only = first_only
        self.render = render
        self.interval = interval

        self.actions = actions
        self.conditions = conditions or []

        if condition_logic not in ('and', 'or'):
            condition_logic = 'and'
        self.condition_logic = condition_logic

        self._id = self._generate_id()

        self._key_content = f'{self._id}:content'
        self._key_last_checked = f'{self._id}:last_checked'

    def _generate_id(self):
        actions = (str(len(self.actions)) + ''.join(f'{a.ACTION_TYPE}'
                                                    for a in self.actions))
        conditions = (str(len(self.conditions)) + str(self.condition_logic) +
                      ''.join(f'{c.cond}{c.cond_type}{c.rule}'
                              for c in self.conditions))

        m = hashlib.sha256()
        m.update((f'{self.url},{self.css_selector},{self.first_only},'
                  f'{self.interval},{actions},{conditions},{self.name}'
                  ).encode('utf-8'))

        return m.hexdigest()

    async def execute_task(self):
        logger.info(f'Executing task {self.name} with ID {self._id}')
        await self._execute_task()
        logger.info(f'Done processing task {self._id}')

    async def _execute_task(self):
        interval_passed = await self._interval_passed()

        if not interval_passed:
            return

        prev_content = await self._get_previous_content()
        current_content = self._get_new_content()

        if current_content == prev_content:
            logger.info(f"Content hasn't changed for task {self._id}")
        else:
            full_diff, added_text, removed_text = self._diff_content(
                prev_content, current_content)

            conditions_met = self._process_conditions(current_content,
                                                      added_text, removed_text)

            if conditions_met:
                logger.info(f"Conditions were met for {self._id}")
                await self._process_actions(full_diff)
            else:
                logger.info(f'Conditions not met for {self._id}')

            await get_redis_client().set(self._key_content, current_content)

        await get_redis_client().set(self._key_last_checked, int(time.time()))

    async def _interval_passed(self) -> bool:
        now = int(time.time())

        last_checked = await get_redis_client().get(self._key_last_checked)
        last_checked = int(last_checked or (now - self.interval))

        if (now - last_checked) < self.interval:
            logger.info(f"Interval not passed yet for task {self._id}")
            return False
        return True

    async def _get_previous_content(self) -> str:
        prev_text = await get_redis_client().get(self._key_content)
        return prev_text.decode() if prev_text else ''

    def _get_new_content(self) -> str:
        found_content = get_content(self.url, css_selector=self.css_selector,
                                    first_only=self.first_only,
                                    render=self.render)

        return '\n'.join(content.text for content in found_content)

    def _diff_content(self, prev_content: str,
                      current_content: str) -> Tuple[str, str, str]:
        diff = difflib.ndiff(
            prev_content.splitlines(keepends=True),
            current_content.splitlines(keepends=True))

        diff = ''.join(diff)
        added_text = ''.join(l[2:] for l in diff if l.startswith('+ '))
        removed_text = ''.join(l[2:] for l in diff if l.startswith('- '))

        return diff, added_text, removed_text

    def _process_conditions(self, text: str, new_text: str,
                            removed_text: str) -> bool:
        test_results = []

        for condition in self.conditions:
            text_to_test = None
            if condition.cond_type == CONDITION_TYPE.TEXT.value:
                text_to_test = text
            elif condition.cond_type == CONDITION_TYPE.ADDED_TEXT.value:
                text_to_test = new_text
            elif condition.cond_type == CONDITION_TYPE.PREVIOUS_TEXT.value:
                text_to_test = removed_text

            if condition.cond == CONDITION.HAS.value:
                test_results.append(condition.rule in text_to_test)
            elif condition.cond == CONDITION.DOES_NOT_HAVE.value:
                test_results.append(condition.rule not in text_to_test)
            elif condition.cond == CONDITION.NOT_EMPTY.value:
                test_results.append(text_to_test)
            elif condition.cond == CONDITION.MATCHES_REGEX.value:
                regex = re.compile(condition.rule)
                test_results.append(regex.match(text_to_test))

        if self.condition_logic == 'or':
            return any(test_results)

        return all(test_results)

    async def _process_actions(self, diff: str):
        for action in self.actions:
            if isinstance(action, ActionEmail):
                await action.send_email(self.url, self.name, diff)
            elif isinstance(action, ActionTelegram):
                action.send_telegram_message(self.url)
