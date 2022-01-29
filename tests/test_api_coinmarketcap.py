#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2022 Bumsoo Kim <bskim45@gmail.com>
#
# MIT Licence http://opensource.org/licenses/MIT

from __future__ import print_function, unicode_literals

from unittest import TestCase

from api import CoinMarketCapClient


class CryptoCompareClientTest(TestCase):
    pass


class CoinMarketCapClientTest(TestCase):
    def test_get_coin_web_url(self):
        self.assertEqual(
            'https://coinmarketcap.com/currencies/ethereum/',
            CoinMarketCapClient.get_coin_web_url('Ethereum'),
        )

    def test_normalize_to_underscore(self):
        self.assertEqual(
            'Binance-Coin',
            CoinMarketCapClient.normalize_to_underscore('Binance Coin'),
        )
