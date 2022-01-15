#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2022 Bumsoo Kim <bskim45@gmail.com>
#
# MIT Licence http://opensource.org/licenses/MIT

from __future__ import print_function, unicode_literals

import json
from unittest import TestCase

import mock

from api import CryptoCompareClient, CoinTick, CoinInfo


def _load_example(path):
    with open(path, 'r') as f:
        payload = json.load(f)

    return payload


class CryptoCompareClientTest(TestCase):
    def setUp(self):
        self.example_market_cap = \
            _load_example('examples/cryptocompare/mktcapfull_10.json')
        self.example_tick_prices_btc_eth = \
            _load_example('examples/cryptocompare/pricemultifull_btceth.json')
        self.example_coinlist_eth = \
            _load_example('examples/cryptocompare/coinlist_eth.json')

    @mock.patch('api.web.get', autospec=True)
    def test_get_tick_prices(
        self,
        mock_get,  # type: mock.MagicMock
    ):
        mock_res = mock_get.return_value
        mock_res.ok.return_value = True
        mock_res.json.return_value = self.example_tick_prices_btc_eth

        api = CryptoCompareClient()
        res = api.get_coin_prices(['BTC', 'ETH'], 'USD')

        mock_get.assert_called()

        expected = [
            CoinTick(
                'BTC', 'Ƀ',
                'https://www.cryptocompare.com/media/37746251/btc.png',
                'USD', '$',
                '43,022.2', '43,355.5', '41,761.2',
                '-253.25', '-0.59',
                '158.53 K', '6.81 B',
            ),
            CoinTick(
                'ETH', 'Ξ',
                'https://www.cryptocompare.com/media/37746238/eth.png',
                'USD', '$',
                '3,271.17', '3,313.47', '3,189.17',
                '-31.25', '-0.95',
                '1.37 M', '4.49 B',
            )
        ]

        self.assertListEqual(res, expected)

    @mock.patch('api.web.get', autospec=True)
    def test_get_top_market_cap(
        self,
        mock_get,  # type: mock.MagicMock
    ):
        mock_res = mock_get.return_value
        mock_res.ok.return_value = True
        mock_res.json.return_value = self.example_market_cap

        api = CryptoCompareClient()
        res = api.get_top_market_cap('USD', 10)

        self.assertEqual(len(res), 10)

    @mock.patch('api.web.get', autospec=True)
    def test_get_coin_info(
        self,
        mock_get,  # type: mock.MagicMock
    ):
        mock_res = mock_get.return_value
        mock_res.ok.return_value = True
        mock_res.json.return_value = self.example_coinlist_eth

        api = CryptoCompareClient()
        res = api.get_coin_info('ETH')

        expected = CoinInfo(
            'Ethereum', 'ETH', None,
            'https://www.cryptocompare.com/media/37746238/eth.png',
            'https://www.cryptocompare.com/coins/eth/overview'
        )
        self.assertEqual(res, expected)
