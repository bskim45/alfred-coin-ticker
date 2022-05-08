#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2022 Bumsoo Kim <bskim45@gmail.com>
#
# MIT Licence http://opensource.org/licenses/MIT

from __future__ import annotations

from unittest import TestCase

from utils import clean_price_string, get_display_change_string


class CleanPriceTest(TestCase):
    def test_simple(self):
        self.assertEqual(clean_price_string('$', '$ 43,107.7'), '43,107.7')

    def test_price_is_empty(self):
        self.assertEqual(clean_price_string('$', ''), '')

    def test_symbol_is_empty(self):
        self.assertEqual(clean_price_string('', '$ 43,107.7'), '$ 43,107.7')

    def test_wrong_symbol(self):
        self.assertEqual(clean_price_string('Ƀ', '$ 43,107.7'), '$ 43,107.7')

    def test_no_symbol_in_price(self):
        self.assertEqual(clean_price_string('Ƀ', '43,107.7'), '43,107.7')


class DisplayChangeStringTest(TestCase):
    def test_simple(self):
        self.assertEqual(get_display_change_string('3.0'), '📈3.0')
        self.assertEqual(get_display_change_string('+3.0'), '📈3.0')
        self.assertEqual(get_display_change_string('-3.0'), '📉3.0')
