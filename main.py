#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2022 Bumsoo Kim <bskim45@gmail.com>
#
# MIT Licence http://opensource.org/licenses/MIT

from __future__ import print_function, unicode_literals, division

import multiprocessing
import sys
from multiprocessing.pool import ThreadPool

from api import CryptoCompareClient, CoinTick, CoinInfo, CoinMarketCapClient
from utils import create_workflow, cached_file, get_display_change_string, \
    cached_file_fresh
from workflow import Workflow3, ICON_INFO, ICON_WEB, web, \
    ICON_SETTINGS, ICON_ERROR, ICON_TRASH

TICKER_CACHE_AGE_SECONDS = 14 * 24 * 60 * 60  # 2 weeks


class Command(object):
    def __init__(self, command_id, alfred_command, help_message, icon=None):
        # type: (unicode, unicode, unicode, unicode) -> Command
        self.command_id = command_id
        self.alfred_command = alfred_command
        self.help_message = help_message
        self.icon = icon

    def is_command(self, command):
        # type: (unicode) -> bool
        return command == self.alfred_command


CMD_LIST_FAVORITES = Command('list_favorites', '', 'List favorite coins.')
CMD_LIST_RANKINGS = Command('list_rankings', 'list',
                            'Toplist by Market Cap.')
CMD_SET_CURRENCY = Command('set_currency', 'set currency', 'Set currency',
                           ICON_SETTINGS)
CMD_HELP = Command('show_help', 'help', 'Show help', ICON_INFO)
CMD_RESET = Command('reset', 'reset',
                    'Reset all settings and delete all caches/data.',
                    ICON_TRASH)
CMD_ADD_COIN = Command('add_coin', 'add', 'Add new coin to the favorites.')
CMD_REMOVE_COIN = Command('remove_coin', 'remove',
                          'Remove a coin from the favorites.')

COMMAND_LIST = [
    CMD_LIST_FAVORITES,
    CMD_LIST_RANKINGS,
    CMD_SET_CURRENCY,
    CMD_ADD_COIN,
    CMD_REMOVE_COIN,
    CMD_RESET,
    CMD_HELP,
]

SETTING_COMMAND_LIST = [
    CMD_SET_CURRENCY,
]


def add_default_item(wf):
    for service in [CoinMarketCapClient, CryptoCompareClient]:
        wf.add_item(
            title='Go to {0}'.format(service.SERVICE_NAME),
            subtitle=service.WEB_BASE_URL,
            arg=service.WEB_BASE_URL,
            valid=True,
            icon=ICON_WEB,
        )

    wf.add_item(
        title=CMD_HELP.help_message,
        subtitle=CMD_HELP.alfred_command,
        autocomplete=CMD_HELP.alfred_command,
        icon=CMD_HELP.icon,
    )


def get_coin_infos_multi(tickers):
    def get_info(ticker):
        api = CryptoCompareClient()
        ticker_info = api.get_coin_info(ticker)
        return ticker_info

    pool = ThreadPool(multiprocessing.cpu_count() // 2)
    coin_infos = pool.map(get_info, tickers)
    return coin_infos


def get_coin_image_multi(ticker_and_image_urls):
    # type: (list[tuple[unicode, unicode]]) -> list[tuple[unicode, str]]  # noqa
    def get_image(ticker_and_image_url):
        ticker, image_url = ticker_and_image_url
        return ticker, web.get(image_url).content

    pool = ThreadPool(multiprocessing.cpu_count() // 2)
    ticker_and_images = pool.map(get_image, ticker_and_image_urls)
    return ticker_and_images


def get_coin_info_from_tickers(wf, tickers):
    # type: (Workflow3, list[unicode]) -> dict[unicode, CoinInfo]  # noqa

    ticker_map = {}
    unknown_tickers = []

    def get_cache_key(ticker):
        return '{0}_info'.format(ticker.lower()).encode('utf-8')

    for ticker in tickers:
        is_cached = wf.cached_data_fresh(
            get_cache_key(ticker), TICKER_CACHE_AGE_SECONDS
        )  # type: CoinInfo

        if is_cached:
            ticker_info = wf.cached_data(get_cache_key(ticker), None,
                                         TICKER_CACHE_AGE_SECONDS)
            ticker_map[ticker] = ticker_info
        else:
            unknown_tickers.append(ticker)

    unknown_coin_info_list = get_coin_infos_multi(unknown_tickers)

    for ticker_info in unknown_coin_info_list:
        # replace web link to coinmarketcap
        ticker_info = ticker_info._replace(  # noqa
            url=CoinMarketCapClient.get_coin_web_url(
                ticker_info.name.lower())
        )
        wf.cached_data(get_cache_key(ticker_info.ticker), lambda: ticker_info,
                       TICKER_CACHE_AGE_SECONDS)
        ticker_map[ticker_info.ticker] = ticker_info

    return ticker_map


def get_coin_image_from_tickers(wf, ticker_and_image_list):
    # type: (Workflow3, list[tuple[unicode, unicode]]) -> dict[unicode, unicode]  # noqa

    ticker_image_path_map = {}
    unknown_ticker_and_image_urls = []

    def get_cache_key(ticker):
        return '{0}_image'.format(ticker.lower()).encode('utf-8')

    for ticker, image_url in ticker_and_image_list:
        is_cached = cached_file_fresh(wf, get_cache_key(ticker),
                                      TICKER_CACHE_AGE_SECONDS)

        if is_cached:
            image_path = cached_file(wf, get_cache_key(ticker), None,
                                     TICKER_CACHE_AGE_SECONDS)
            ticker_image_path_map[ticker] = image_path
        else:
            unknown_ticker_and_image_urls.append((ticker, image_url))

    unknown_ticker_image_list = get_coin_image_multi(
        unknown_ticker_and_image_urls)

    for ticker, image in unknown_ticker_image_list:
        image_path = cached_file(wf, get_cache_key(ticker), lambda: image,
                                 TICKER_CACHE_AGE_SECONDS)
        ticker_image_path_map[ticker] = image_path

    return ticker_image_path_map


def add_ticks_to_workflow(wf, ticks):
    # type: (Workflow3, list[CoinTick]) -> bool  # noqa

    coin_info_map = get_coin_info_from_tickers(
        wf, [tick.ticker for tick in ticks]
    )

    coin_image_path_map = get_coin_image_from_tickers(
        wf, [(tick.ticker, tick.image_url) for tick in ticks]
    )

    for tick in ticks:
        item = wf.add_item(
            title='{ticker:<5}\t{fiat}{price:10}\t({change_pct}%) \t{symbol} {volume}'.format(
                # noqa
                ticker=tick.ticker, fiat=tick.fiat_symbol, price=tick.price,
                change_pct=get_display_change_string(
                    tick.price_change_24h_percent),
                symbol=tick.symbol,
                volume=tick.total_volume_24h,
            ),
            subtitle='24h High {0}{1} | Low {0}{2}  | Change {3}'.format(
                tick.fiat_symbol,
                tick.price_24h_high, tick.price_24h_low,
                get_display_change_string(tick.price_change_24h),
            ),
            arg=coin_info_map[tick.ticker].url,
            valid=True,
            icon=coin_image_path_map[tick.ticker],
        )
        item.add_modifier('cmd', 'Copy ticker price',
                          arg=tick.price.replace(',', ''))
        item.add_modifier('alt', 'Copy ticker', arg=tick.ticker)

    return len(ticks) > 0


def list_rankings(wf):
    # type: (Workflow3) -> ()

    fiat = wf.settings.get('currency')

    def _get():
        api = CryptoCompareClient()
        return api.get_top_market_cap(fiat, 10)

    add_ticks_to_workflow(
        wf,
        wf.cached_data(b'market_cap_rankings_10', _get, max_age=3, session=True)
    )


def list_tickers(wf, tickers):
    # type: (Workflow3, list[unicode]) -> ()  # noqa
    if not tickers:
        return

    fiat = wf.settings.get('currency')

    def _get():
        api = CryptoCompareClient()
        return api.get_coin_prices(tickers, fiat)

    is_not_empty = add_ticks_to_workflow(
        wf,
        wf.cached_data(b'tickers_{0}'.format('_'.join(tickers)), _get,
                       max_age=3, session=True),
    )

    return is_not_empty


def list_favorites(wf):
    # type: (Workflow3) -> ()
    favorite_coins = wf.settings.get('favorites', [])
    list_tickers(wf, favorite_coins)


def show_help(wf):
    # type: (Workflow3) -> ()
    for cmd in COMMAND_LIST:
        wf.add_item(
            title=cmd.help_message,
            subtitle='coin ' + cmd.alfred_command,
            autocomplete=cmd.alfred_command,
        )


def show_setting_help(wf):
    # type: (Workflow3) -> ()
    for cmd in SETTING_COMMAND_LIST:
        wf.add_item(
            title=cmd.help_message,
            subtitle='coin ' + cmd.alfred_command,
            autocomplete=cmd.alfred_command,
            icon=ICON_SETTINGS,
        )


def show_add_favorites_help(wf):
    # type: (Workflow3) -> ()
    wf.add_item(
        title='coin add [TICK]',
        subtitle='Add the coin at the end of the list.',
        autocomplete='add ',
        icon=ICON_INFO,
    )
    wf.add_item(
        title='coin add [TICK] [POSITION]',
        subtitle='Add the coin at the position.',
        autocomplete='add ',
        icon=ICON_INFO,
    )


def add_favorites_prompt(wf, ticker, position_str=None):
    # type: (Workflow3, unicode, Optional[unicode]) -> ()  # noqa

    ticker = ticker.upper()
    favorites = wf.settings['favorites']  # type: list[unicode]  # noqa

    if ticker in favorites:
        wf.add_item(
            title="'{0}' is already in the favorites.".format(ticker),
            subtitle='press ENTER to show coin prices',
            autocomplete='',
            icon=ICON_INFO,
        )
    else:
        position = None
        if position_str:
            try:
                position = int(position_str)
            except ValueError:
                position = None

        if position:
            wf.add_item(
                title="Add '{0}' to the favorites at position {1}.".format(
                    ticker, position),
                subtitle='press ENTER to proceed',
                autocomplete='add_commit {0} {1}'.format(ticker, position),
                icon=ICON_INFO,
            )
        else:
            wf.add_item(
                title="Add '{0}' to the end of the favorites.".format(
                    ticker, position),
                subtitle='press ENTER to proceed',
                autocomplete='add_commit {0}'.format(ticker, position),
                icon=ICON_INFO,
            )


def add_favorites(wf, ticker, position_str=None):
    # type: (Workflow3, unicode, Optional[unicode]) -> ()  # noqa

    ticker = ticker.upper()
    favorites = wf.settings['favorites']  # type: list[unicode]  # noqa

    position = int(position_str) if position_str else None
    if position:
        favorites.insert(position - 1, ticker)
    else:
        favorites.append(ticker)

    wf.settings['favorites'] = favorites
    wf.settings.save()

    wf.add_item(
        title="'{0}' is added to the favorites.".format(ticker),
        subtitle='press ENTER to show coin prices',
        autocomplete='',
        icon=ICON_INFO,
    )


def remove_favorites(wf, ticker):
    # type: (Workflow3, unicode) -> ()  # noqa

    ticker = ticker.upper()
    favorites = wf.settings['favorites']  # type: list[unicode]  # noqa

    if ticker in favorites:
        favorites.remove(ticker)
        wf.settings['favorites'] = favorites
        wf.settings.save()

    wf.add_item(
        title="'{0}' is removed from the favorites.".format(ticker),
        subtitle='press ENTER to show coin prices',
        autocomplete='',
        icon=ICON_INFO,
    )


def set_currency(wf, fiat):
    # type: (Workflow3, Optional[unicode]) -> ()  # noqa
    if not fiat:
        wf.warn_empty(
            title='Set currency',
            subtitle='coin set currency [CURRENCY] (3 letters)',
            icon=ICON_SETTINGS,
        )

    else:
        fiat = fiat.upper()

        if len(fiat) != 3:
            wf.warn_empty(title="'{0}' is invalid currency.".format(fiat),
                          icon=ICON_ERROR)
        else:
            wf.settings['currency'] = fiat
            wf.add_item(
                title="Currency is set to '{0}'.".format(fiat),
                subtitle='press ENTER to show coin prices',
                autocomplete='',
                icon=ICON_INFO,
            )


def prompt_reset(wf):
    wf.add_item(
        title='Are you sure you want to reset all settings/data to default?',
        subtitle='press ENTER to confirm',
        autocomplete='reset all',
        icon=ICON_ERROR,
    )


def reset_all(wf):
    try:
        wf.clear_settings()
    except:  # noqa
        wf.logger.exception('clear settings failed')

    try:
        wf.clear_data()
    except:  # noqa
        wf.logger.exception('clear data failed')

    try:
        wf.clear_cache()
    except:  # noqa
        wf.logger.exception('clear cache failed')

    wf.add_item(
        title='All settings/data is set to default.',
        subtitle='press ENTER to show coin prices',
        autocomplete='',
        icon=ICON_INFO,
    )


def main(wf):
    # type: (Workflow3) -> int

    wf.logger.info('user args: "%s"', wf.args)

    show_default_items = False

    if len(wf.args) == 0:
        list_favorites(wf)

    else:
        command = wf.args[0]

        if len(command) == 0:
            list_favorites(wf)

        elif CMD_LIST_RANKINGS.is_command(command):
            list_rankings(wf)

        elif CMD_ADD_COIN.is_command(command):
            if len(wf.args) == 2:
                add_favorites_prompt(wf, *wf.args[1:])
            elif len(wf.args) == 3:
                add_favorites_prompt(wf, *wf.args[1:])
            else:
                show_add_favorites_help(wf)

        elif command == 'add_commit':
            if len(wf.args) == 2 or len(wf.args) == 3:
                add_favorites(wf, *wf.args[1:])
            else:
                show_default_items = True

        elif CMD_REMOVE_COIN.is_command(command):
            if len(wf.args) == 2:
                remove_favorites(wf, wf.args[1])
            else:
                show_default_items = True

        elif CMD_HELP.is_command(command):
            show_help(wf)

        elif CMD_RESET.is_command(command):
            if len(wf.args) == 2 and wf.args[1]:
                reset_all(wf)
            else:
                prompt_reset(wf)

        elif command == 'set':
            if len(wf.args) == 1:
                show_setting_help(wf)
            else:
                subcommand = wf.args[1]

                if subcommand == 'currency':
                    if len(wf.args) == 3:
                        set_currency(wf, wf.args[2])
                    elif len(wf.args) == 2:
                        set_currency(wf, None)
                else:
                    show_setting_help(wf)

        elif command.startswith('workflow:'):
            pass

        else:
            # single coin price
            if len(wf.args) == 1:
                if len(wf.args[0]) < 3:
                    show_default_items = True
                else:
                    is_not_empty = list_tickers(wf, [wf.args[0].upper()])
                    show_default_items = not is_not_empty
            else:
                show_default_items = True

    if wf.update_available:
        wf.add_item('New version is available',
                    subtitle='Click to install the update',
                    autocomplete='workflow:update',
                    icon=ICON_INFO)

    if show_default_items:
        add_default_item(wf)

    wf.send_feedback()
    return 0


if __name__ == '__main__':
    _wf = create_workflow()
    sys.exit(_wf.run(main))
