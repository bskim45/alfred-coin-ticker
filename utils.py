#!/usr/bin/env python3
# encoding: utf-8
#
# Copyright (c) 2022 Bumsoo Kim <bskim45@gmail.com>
#
# MIT Licence http://opensource.org/licenses/MIT

from __future__ import annotations

import os
import time

from workflow import Workflow3
from workflow.util import atomic_writer


def create_workflow():
    # type: () -> Workflow3
    wf = Workflow3(
        default_settings={
            'currency': 'USD',
            'favorites': [
                'BTC',
                'ETH',
                'XRP',
                'BNB',
                'SOL',
                'DOGE',
                'ADA',
                'TRX',
                'AVAX',
                'XLM',
            ],
        },
        update_settings={
            'github_slug': 'bskim45/alfred-coin-ticker',
            'frequency': 7,  # once a week
        },
    )

    wf.settings.save()
    return wf


def clean_price_string(symbol, price_str):
    # type: (str, str) -> str
    if not symbol or not price_str:
        return price_str

    return price_str.lstrip(symbol).strip()


def get_display_change_string(change_str):
    # type: (str) -> str
    if not change_str.startswith('-') and not change_str.startswith('+'):
        return '📈' + change_str
    elif change_str.startswith('+'):
        return '📈' + change_str[1:]
    else:
        return '📉' + change_str[1:]


def cached_file_age(wf, name):
    # type: (Workflow3, str) -> int
    cache_path = wf.cachefile(name)
    if not os.path.exists(cache_path):
        return 0

    return int(time.time() - os.stat(cache_path).st_mtime)


def cached_file_fresh(wf, name, max_age):
    # type: (Workflow3, str, int) -> bool
    age = cached_file_age(wf, name)

    if not age:
        return False

    return age < max_age


def cache_file(wf, name, data):
    # type: (Workflow3, str, str) -> ()

    cache_path = wf.cachefile(name)

    if data is None:
        if os.path.exists(cache_path):
            os.unlink(cache_path)
            wf.logger.debug('deleted cache file: %s', cache_path)
        return

    with atomic_writer(cache_path, 'wb') as file_obj:
        file_obj.write(data)

    wf.logger.debug('cached file: %s', cache_path)


def cached_file(wf, name, data_func=None, max_age=60):
    # type: (Workflow3, str, callable, int) -> Optional[str]  # noqa

    cache_path = wf.cachefile(name)
    age = cached_file_age(wf, name)

    if (age < max_age or max_age == 0) and os.path.exists(cache_path):
        wf.logger.debug('found cached data: %s', cache_path)
        return cache_path

    if not data_func:
        return None

    data = data_func()
    cache_file(wf, name, data)

    return cache_path
