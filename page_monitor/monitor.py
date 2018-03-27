import asyncio
import logging
from typing import List

import click
import yaml

from page_monitor.actions import ActionEmail, ActionTelegram
from page_monitor.conditions import Condition
from page_monitor.config import set_config, init_redis
from page_monitor.tasks import Task

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s %(name)s - %(message)s")

loop = asyncio.get_event_loop()


@click.command()
@click.argument('tasks_file', type=click.Path(exists=True))
def run_monitor(tasks_file):

    with open(tasks_file) as f:
        _raw_tasks = yaml.load(f.read())
        tasks = _raw_tasks['tasks']
        set_config(_raw_tasks)

    processed_tasks = []
    for task in tasks:
        click.echo(task['url'])

        actions = []
        for action in task['actions']:
            action_type = action['type']
            params = action.get('params', {})
            if action_type == ActionEmail.ACTION_TYPE:
                actions.append(ActionEmail(params['email_to']))
            elif action_type == ActionTelegram.ACTION_TYPE:
                actions.append(
                    ActionTelegram(str(params['chat_id']), params['token']))
            else:
                click.echo(
                    click.style(f"Unrecognized action type {action.keys()[0]}",
                                fg='orange'))

        # Process conditions here
        conditions = []
        for condition in task.get('conditions', []):
            conditions.append(
                Condition(condition['type'], condition['cond'],
                          str(condition.get('rule', ''))))

        processed_tasks.append(
            Task(task['url'], task['css_selector'], task.get('interval', 3600),
                 actions, conditions=conditions,
                 first_only=task.get('first_only', False),
                 condition_logic=task.get('condition_logic'),
                 name=task.get('name'), render=task.get('render', False)))

    loop.run_until_complete(run_tasks(processed_tasks))
    loop.close()


async def run_tasks(tasks: List[Task]):
    await init_redis()
    while True:
        for task in tasks:
            await task.execute_task()
        await asyncio.sleep(5)


if __name__ == '__main__':
    run_monitor()
