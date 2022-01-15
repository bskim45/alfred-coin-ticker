#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2022 Bumsoo Kim <bskim45@gmail.com>
#
# MIT Licence http://opensource.org/licenses/MIT

from __future__ import print_function, unicode_literals

import os
from collections import namedtuple

from utils import clean_price_string
from workflow import web


class CoinTick(object):
    def __init__(
        self,
        ticker,  # type: unicode
        symbol,  # type: unicode
        image_url,  # type: unicode
        fiat,  # type: unicode
        fiat_symbol,  # type: unicode
        price,  # type: unicode
        price_24h_high,  # type: unicode
        price_24h_low,  # type: unicode
        price_change_24h,  # type: unicode
        price_change_24h_percent,  # type: unicode
        total_volume_24h,  # type: unicode
        total_volume_24h_fiat,  # type: unicode
    ):
        self.ticker = ticker
        self.symbol = symbol
        self.image_url = image_url
        self.fiat = fiat
        self.fiat_symbol = fiat_symbol
        self.price = price
        self.price_24h_high = price_24h_high
        self.price_24h_low = price_24h_low
        self.price_change_24h = price_change_24h
        self.price_change_24h_percent = price_change_24h_percent
        self.total_volume_24h = total_volume_24h
        self.total_volume_24h_fiat = total_volume_24h_fiat

    def __eq__(self, o):
        if not isinstance(o, CoinTick):
            return False

        return all((
            self.ticker == o.ticker,
            self.symbol == o.symbol,
            self.image_url == o.image_url,
            self.fiat == o.fiat,
            self.fiat_symbol == o.fiat_symbol,
            self.price == o.price,
            self.price_24h_high == o.price_24h_high,
            self.price_24h_low == o.price_24h_low,
            self.price_change_24h == o.price_change_24h,
            self.price_change_24h_percent == o.price_change_24h_percent,
            self.total_volume_24h == o.total_volume_24h,
            self.total_volume_24h_fiat == o.total_volume_24h_fiat,
        ))

    def __unicode__(self):
        return '{0} {1} ({2}{3})'.format(
            self.symbol, self.ticker, self.fiat_symbol, self.price)

    def __str__(self):
        return unicode(self).encode('utf-8')


CoinInfo = namedtuple(
    'CoinInfo',
    ['name', 'ticker', 'symbol', 'image_url', 'url']
)


class TickClient(object):
    SERVICE_NAME = None
    CACHE_KEY = None
    API_BASE_URL = None
    WEB_BASE_URL = None

    @classmethod
    def get_cache_key(cls, query=None):
        return '{0}-{1}'.format(cls.CACHE_KEY, query) \
            .replace(os.sep, '_')

    def get(self, path, params):
        # type: (unicode, dict) -> dict
        r = web.get(self.API_BASE_URL + path, params)
        r.raise_for_status()

        result = r.json()
        return result

    def get_coin_prices(self, tickers, fiat):
        # type: (list[unicode], unicode) -> list[CoinTick]  # noqa
        raise NotImplementedError()

    def get_top_market_cap(self, limit, fiat):
        # type: (int, unicode) -> list[CoinTick]  # noqa
        raise NotImplementedError()

    def get_coin_info(self, ticker):
        # type: (unicode) -> CoinInfo  # noqa
        raise NotImplementedError()

    def get_ticker_web_url(self, ticker, fiat):
        # type: (unicode, unicode) -> unicode
        raise NotImplementedError()


class CryptoCompareClient(TickClient):
    SERVICE_NAME = 'CryptoCompare'
    CACHE_KEY = SERVICE_NAME.lower()
    API_BASE_URL = 'https://min-api.cryptocompare.com/data'
    WEB_BASE_URL = 'https://www.cryptocompare.com'

    def get(self, path, params):
        result = super(CryptoCompareClient, self).get(path, params)

        if 'Response' in result and result.get('Response') != 'Success':
            raise Exception(result.get('Message'))

        return result

    def get_coin_prices(self, tickers, fiat):
        # ex. https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC&tsyms=USD # noqa

        params = dict(fsyms=tickers, tsyms=fiat)
        res = self.get('/pricemultifull', params)

        return [
            self.tick_from_api_repr(
                res['RAW'][tick][fiat],
                res['DISPLAY'][tick][fiat],
            )
            for tick in tickers
        ]

    def get_top_market_cap(self, fiat, limit):
        # ex. https://min-api.cryptocompare.com/data/top/mktcapfull?limit=10&tsym=USD  # noqa

        params = dict(limit=limit, tsym=fiat)
        res = self.get('/top/mktcapfull', params)

        return [
            self.tick_from_api_repr(r['RAW'][fiat], r['DISPLAY'][fiat])
            for r in res.get('Data', [])
        ]

    def get_coin_info(self, ticker):
        # ex. https://min-api.cryptocompare.com/data/all/coinlist?fsym=ETH

        params = dict(fsym=ticker.upper())
        res = self.get('/all/coinlist', params)

        return self.coin_info_from_api_repr(res['Data'][ticker])

    def get_ticker_web_url(self, ticker, fiat):
        return '{0}/coins/{1}/overview/{2}'.format(
            self.WEB_BASE_URL, ticker.lower(), fiat.upper()
        )

    @classmethod
    def coin_info_from_api_repr(cls, data):
        # type: (dict) -> CoinInfo
        return CoinInfo(
            data['CoinName'], data['Symbol'], None,
            cls.WEB_BASE_URL + data['ImageUrl'],
            cls.WEB_BASE_URL + data['Url']
        )

    @classmethod
    def tick_from_api_repr(cls, raw, display):
        # type: (dict, dict) -> CoinTick

        ticker = raw.get('FROMSYMBOL')
        symbol = display.get('FROMSYMBOL')
        fiat = raw.get('TOSYMBOL')
        fiat_symbol = display.get('TOSYMBOL')

        return CoinTick(
            ticker, symbol,
            cls.WEB_BASE_URL + display.get('IMAGEURL'),
            fiat, fiat_symbol,
            clean_price_string(fiat_symbol, display.get('PRICE')),
            clean_price_string(fiat_symbol, display.get('HIGH24HOUR')),
            clean_price_string(fiat_symbol, display.get('LOW24HOUR')),
            clean_price_string(fiat_symbol, display.get('CHANGE24HOUR')),
            display.get('CHANGEPCT24HOUR'),
            clean_price_string(symbol, display.get('TOTALVOLUME24H')),
            clean_price_string(fiat_symbol, display.get('TOTALVOLUME24HTO')),
        )


class CoinMarketCapClient(TickClient):
    SERVICE_NAME = 'CoinMarketCap'
    CACHE_KEY = SERVICE_NAME.lower()
    API_BASE_URL = 'https://pro-api.coinmarketcap.com'
    WEB_BASE_URL = 'https://coinmarketcap.com'

    def get_coin_prices(self, tickers, fiat):
        raise NotImplementedError()

    def get_top_market_cap(self, limit, fiat):
        raise NotImplementedError()

    def get_coin_info(self, tickers):
        raise NotImplementedError()

    def get_ticker_web_url(self, ticker, fiat):
        raise NotImplementedError()

    @classmethod
    def get_coin_web_url(cls, coin_name):
        return '{0}/currencies/{1}/'.format(
            cls.WEB_BASE_URL, coin_name.lower()
        )
