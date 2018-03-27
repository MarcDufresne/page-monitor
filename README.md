# Page Monitor

[![Build Status](https://travis-ci.org/MarcDufresne/page-monitor.svg?branch=master)](https://travis-ci.org/MarcDufresne/page-monitor)
![PyPI](https://img.shields.io/pypi/v/page-monitor.svg)
![PyPI - License](https://img.shields.io/pypi/l/page-monitor.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/page-monitor.svg)
![PyPI - Status](https://img.shields.io/pypi/status/page-monitor.svg)
![GitHub issues](https://img.shields.io/github/issues/MarcDufresne/page-monitor.svg)


_(If you are reading this on PyPI you can go on the
[project's GitHub page](https://github.com/MarcDufresne/page-monitor)
for a properly formatted version)_

This is an app that monitors web pages for changes,
with optional conditions, and is able to execute actions
based on changes, like send an email or a Telegram message.

It will also **fully support JavaScript** rendering by using Chromium
in the background once `requests-html` releases an Async compatible
version.

## Quickstart

1. `pip install page-monitor`
2. Create a tasks configuration file
3. `page_monitor tasks.yml`

## Documentation

Documentation available on
[Read The Docs](http://page-monitor.readthedocs.io/en/latest/)

Documentation source
[here](https://github.com/MarcDufresne/page-monitor/tree/master/docs)
