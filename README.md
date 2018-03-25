# Page Monitor

_(If you are reading this on PyPI you can go on the
[project's GitHub page](https://github.com/MarcDufresne/page-monitor)
for a properly formatted version)_

This is an app that monitors web pages for changes,
with optional conditions, and is able to execute actions
based on changes, like send an email or a Telegram message.

It will also **fully support JavaScript** rendering by using Chromium
in the background once `requests-html` releases an Async compatible
version.

## Installation

You will need **Python 3.6+** to run this app.

An easy way to install Python 3.6 is to use 
[pyenv](https://github.com/pyenv/pyenv)
(with [pyenv-installer](https://github.com/pyenv/pyenv-installer))

**Install with `pip`**

1. In a Python 3.6+ environment, run `pip install page-monitor`
2. Create a configuration file
3. Run the app according to _Usage_ below

**Clone locally**

1. Clone this repo
2. Create a configuration file
3. Install the contents of `requirements.txt` into a Python 3.6+ environment
4. Run the app according to _Usage_ below

## Usage

**Installed with `pip`**

```
page_monitor <tasks_file>
```

**Cloned locally**

```
python page_monitor/monitor.py <tasks_file>
```

## Configuration

To configure tasks simply create a YAML file containing
your tasks definitions. Here's an example:

```yaml

---
tasks:
  - name: A Page
    url: http://example.com/page_1.html
    css_selector: ".a-class"
    first_only: True
    interval: 60
    actions:
      - email:
          email_to: recipient@domain.com
    conditions:
      - cond_type: text
        cond: has
        rule: "some text"
    condition_logic: and
redis: 127.0.0.1:6379
mailgun:
  domain: mail.domain.com
  api_key: key-aaa111bbb222ccc333
```

### Config options

Here's a definition of the config structure with available
options and default.

- `tasks` _(list)_: List of tasks
  - `name` _(string)_: Name for your task, useful for notifications,
       defaults to `url` if not specified.
  - `url` _(string)_ **Required**: URL of the page to monitor.
  - `css_selector` _(string)_ **Required**: Part of the page to monitor.
  - `first_only` _(boolean)_: If multiple elements match the `css_selector`.
       this will only process the first matched element. Defaults to: `False`.
  - `interval` _(integer)_ **Required**: Interval in seconds for checks,
       minimum of 5 seconds.
  - `render` _(bool)_: Whether to use Chromium to render JavaScript or not,
       defaults to `False`.
  - `actions` _(list)_: List of actions, see below for details.
  - `conditions` _(list)_: List of conditions, see below for details.
       If no conditions are specified actions will be triggered by any
       content change.
  - `condition_logic` _(string)_: Logic to apply to conditions, choices are
       `and` or `or`, defaults to `and`.

To run Page Monitor you will also need a Redis server, you can specify a
connection string in a `host:port` format in a top level `redis` key. The
`redis` config default to `127.0.0.1:6379`, so it can be omitted if using
the default Redis config.

To send emails you will also need to specify a SMTP or Mailgun config.
To do this, specify a top-level `mailgun` or `smtp` config with the
following inside:

- `mailgun`:
  - `domain` _(string)_ **Required**: Your Mailgun domain name.
  - `api_key` _(string)_ **Required**: Your Mailgun API key, starts
       with `key-`.
  - `from_email` _(string)_ **Required**: Email address that will be displayed
       as `From` in notification emails.
  - `from_name` _(string)_: The sender name that will be displayed
       in notification emails. Defaults to `from_email`.

- `smtp`:
  - `host` _(string)_: SMTP server host. Defaults to `smtp.gmail.com`.
  - `port` _(int)_: SMTP server port. Defaults to `587`.
  - `username` _(string)_ **Required**: Username for SMTP server.
  - `password` _(string)_ **Required**: Password for SMTP server.
  - `tls` _(bool)_: Whether to use TLS for server connection.
       Defaults to `True`.
  - `from_email` _(string)_: Email address that will be displayed
       as `From` in notification emails. Can be omitted if using
       GMail's SMTP server as it will rewrite it anyways.


#### Actions

Each item in the action list must first define what type of action
it is, and contain any required or optional parameters for this specific
action.

It should look like this:
```yaml
action_type:
  param_1: value
  param_2: value
```

- `email`: Send an email with content diff when content has changed
     and conditions are met.
  - `email_to` _(string)_ **Required**: Recipient of the notification email.
- `telegram` **Not yet available**: Send a Telegram message when changes
     are detected and conditions are met.

#### Conditions

Each condition has 3 attributes:

- `cond_type` **Required**: Defines what will be evaluated, should be one of the following:
  - `text`: Check will be made on full current content.
  - `added_text`: Check will be made only on added text.
  - `removed_text`: Check will be made only on text that was removed.
- `cond` **Required**: Defines what check will occur, should be one of the following:
    - `not_empty`: Checks that the text is not empty.
    - `has`: Checks that the text contains the specified `rule`.
    - `does_not_have`: Inverse of `has`.
    - `matches_regex`: Check that the text matches the regex specified
         in `rule`.
- `rule` _(string)_: Rule used to check the condition, should be a plain
     string if using `has` or `does_not_have`, or a valid Python regex if
     using `matches_regex` (You can use [Regex 101](https://regex101.com/)
     for help with that).
