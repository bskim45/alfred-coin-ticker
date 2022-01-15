#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2022 Bumsoo Kim <bskim45@gmail.com>
#
# MIT Licence http://opensource.org/licenses/MIT

from __future__ import print_function, unicode_literals

from unittest import TestCase

from api import CoinTick


class CoinTickTest(TestCase):
    def test_operator_eq(self):
        a = CoinTick(
            'BTC', 'Ƀ',
            'https://www.cryptocompare.com/media/37746251/btc.png',
            'USD', '$',
            '43,022.2', '43,355.5', '41,761.2',
            '-253.25', '-0.59',
            '158.53 K', '6.81 B',
        )
        b = CoinTick(
            'BTC', 'Ƀ',
            'https://www.cryptocompare.com/media/37746251/btc.png',
            'USD', '$',
            '43,022.2', '43,355.5', '41,761.2',
            '-253.25', '-0.59',
            '158.53 K', '6.81 B',
        )

        self.assertEqual(a, b)
