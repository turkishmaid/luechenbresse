#!/usr/bin/env python
# coding: utf-8

import unittest
from luechenbresse import text

class TestUndecorate(unittest.TestCase):

    def test_removes_foo_and_adds_one_layer_of_list(self):
        t = [["+A /B", "X-"], "U. V."]
        x = text.undecorate(t)
        u = [[['A', 'B'], ['X']], ['U', 'V']]
        self.assertEqual(x, u)

    def test_keeps_words(self):
        t = ' "Aa. B" '
        x = text.undecorate(t)
        u = ['Aa', 'B']
        self.assertEqual(x, u)

    def test_drops_words_that_are_only_foo(self):
        t = ' "Aa. B" ...'
        x = text.undecorate(t)
        u = ['Aa', 'B']
        self.assertEqual(x, u)

    def test_regression_removes_typographic_quotes(self):
        t = ' “Aa. B” ...'
        x = text.undecorate(t)
        u = ['Aa', 'B']
        self.assertEqual(x, u)

    def test_regression_removes_single_quotes(self):
        t = " 'Aa. B' ..."
        x = text.undecorate(t)
        u = ['Aa', 'B']
        self.assertEqual(x, u)


class TestFlatten(unittest.TestCase):

    def test_flattens_nested_structures_and_leaves_strings_unchanged(self):
        t = [[['A', 'B C+'], ['X ']], "T", ['U', ' V'], "W"]
        x = text.flatten(t)
        u = ['A', 'B C+', 'X ', 'T', 'U', ' V', 'W']
        self.assertEqual(x, u)

    def test_accepts_various_forms_of_nesting_1(self):
        t = [[" +A /B C+", "X-"], "U. V."]
        x = text.flatten(text.undecorate(t))
        u = ['A', 'B', 'C', 'X', 'U', 'V']
        self.assertEqual(x, u)

    def test_accepts_various_forms_of_nesting_2(self):
        t = [["+Aa /B C+ ", ["X-", ";Y"], "-Z"], "U. V."]
        x = text.flatten(text.undecorate(t))
        u = ['Aa', 'B', 'C', 'X', 'Y', 'Z', 'U', 'V']
        self.assertEqual(x, u)

class TestJoin(unittest.TestCase):

    def test_accepts_variable_number_of_args(self):
        self.assertEqual(text.join("A", "B C"), ['A', 'B', 'C'])
        self.assertEqual(text.join("A", "B+ C ", ["D"], [["-Ee.", "F"]]), ['A', 'B', 'C', 'D', 'Ee', 'F'])

    def text_accepts_tuples(self):
        t = ("A", "B+ C ", ["D"], [["-E.", "F"]])
        x = text.join(t)
        u = ['A', 'B', 'C', 'D', 'E', 'F']
        self.assertEqual(x, u)

    def test_accepts_lists(self):
        t = ["A", "B+ C ", ["D"], [["-E.", "F"]]]
        x = text.join(t)
        u = ['A', 'B', 'C', 'D', 'E', 'F']
        self.assertEqual(x, u)

    def test_is_cool(self):
        t = [["+A /B C+", ["D"], [["E", "F"]], ["X-", ";Y"], "-Z"], "U. V."]
        x = text.join(t)
        u = ['A', 'B', 'C', 'D', 'E', 'F', 'X', 'Y', 'Z', 'U', 'V']
        self.assertEqual(x, u)

class TestSJoin(unittest.TestCase):

    def test_is_just_cool(self):
        t = [["+A /B C+", ["Dd..."], [["E", "F"]], ["X-", ";Y"], "-Z"], "U. V."]
        x = text.sjoin(t)
        u = 'A B C Dd E F X Y Z U V'
        self.assertEqual(x, u)

    def test_removes_whitespace(self):
        x = text.sjoin(["A", "B"], [" "], ["C", "D"])
        u = "A B C D"
        self.assertEqual(x, u)

    def test_removes_decoration(self):
        x = text.sjoin(["A", "B"], [" ..."], ["C", "D"])
        u = "A B C D"
        self.assertEqual(x, u)

class TestContext(unittest.TestCase):

    NUMBERS = "null eins zwei drei vier fünf sechs sieben acht neun zehn elf zwölf dreiz vierz fünfz".split()

    def test_smoke_test(self):
        ctx, offset = text.context(self.NUMBERS, 1, 2, width=1)
        self.assertEqual(ctx, "null eins zwei drei ...")
        self.assertEqual(offset, 5)
        self.assertEqual(ctx[offset], self.NUMBERS[1][0])

    def test_not_enough_left(self):
        ctx, offset = text.context(self.NUMBERS, 1, 2, width=3)
        self.assertEqual(ctx, "null eins zwei drei vier fünf ...")
        self.assertEqual(offset, 5)
        self.assertEqual(ctx[offset], self.NUMBERS[1][0])

    def test_not_enough_right(self):
        ctx, offset = text.context(self.NUMBERS, 13, 14, width=3)
        self.assertEqual(ctx, "... zehn elf zwölf dreiz vierz fünfz")
        self.assertEqual(offset, 19)
        self.assertEqual(ctx[offset], self.NUMBERS[13][0])

    def test_ellipsis_start(self):
        ctx, offset = text.context(self.NUMBERS, 13, 14, width=3)
        self.assertEqual(ctx[0:4], "... ")
        self.assertEqual(ctx[offset], self.NUMBERS[13][0])

    def test_ellipsis_end(self):
        ctx, offset = text.context(self.NUMBERS, 1, 2, width=3)
        self.assertEqual(ctx[-4:], " ...")
        self.assertEqual(ctx[offset], self.NUMBERS[1][0])

    def test_term_at_begin(self):
        ctx, offset = text.context(self.NUMBERS, 0, 1, width=3)
        self.assertEqual(ctx, "null eins zwei drei vier ...")
        self.assertEqual(offset, 0)
        self.assertEqual(ctx[offset], self.NUMBERS[0][0])

    def test_term_at_end(self):
        ctx, offset = text.context(self.NUMBERS, 14, 15, width=3)
        self.assertEqual(ctx, "... elf zwölf dreiz vierz fünfz")
        self.assertEqual(offset, 20)
        self.assertEqual(ctx[offset], self.NUMBERS[14][0])

    def test_long_term(self):
        ctx, offset = text.context(self.NUMBERS, 7, 8, width=20)
        self.assertEqual(ctx, " ".join(self.NUMBERS))
        self.assertEqual(offset, 36)
        self.assertEqual(ctx[offset], self.NUMBERS[7][0])

    def test_short_term(self):
        ctx, offset = text.context(self.NUMBERS, 7, 7, width=2)
        self.assertEqual(ctx, "... fünf sechs sieben acht neun ...")
        self.assertEqual(offset, 15)
        self.assertEqual(ctx[offset], self.NUMBERS[7][0])

    def test_short_term_begin(self):
        ctx, offset = text.context(self.NUMBERS, 0, 0, width=1)
        self.assertEqual(ctx, "null eins ...")
        self.assertEqual(offset, 0)
        self.assertEqual(ctx[offset], self.NUMBERS[0][0])

    def test_short_term_end(self):
        ctx, offset = text.context(self.NUMBERS, 15, 15, width=1)
        self.assertEqual(ctx, "... vierz fünfz")
        self.assertEqual(offset, 10)
        self.assertEqual(ctx[offset], self.NUMBERS[15][0])

    def test_negative_term(self):
        ctx, offset = text.context(self.NUMBERS, 8, 7, width=2)
        self.assertEqual(ctx, "... fünf sechs sieben acht neun zehn ...")
        self.assertEqual(offset, 15)
        self.assertEqual(ctx[offset], self.NUMBERS[7][0])

    def test_no_context(self):
        ctx, offset = text.context(self.NUMBERS, 7, 8, width=0)
        self.assertEqual(ctx, "... sieben acht ...")
        self.assertEqual(offset, 4)
        self.assertEqual(ctx[offset], self.NUMBERS[7][0])

    def test_no_context_begin(self):
        ctx, offset = text.context(self.NUMBERS, 0, 0, width=0)
        self.assertEqual(ctx, "null ...")
        self.assertEqual(offset, 0)
        self.assertEqual(ctx[offset], self.NUMBERS[0][0])

    def test_no_context_end(self):
        ctx, offset = text.context(self.NUMBERS, 15, 15, width=0)
        self.assertEqual(ctx, "... fünfz")
        self.assertEqual(offset, 4)
        self.assertEqual(ctx[offset], self.NUMBERS[15][0])

    def test_off_limits_begin(self):
        ctx, offset = text.context(self.NUMBERS, -5, 2, width=1)
        self.assertEqual(ctx, "null eins zwei drei ...")
        self.assertEqual(offset, 0)
        self.assertEqual(ctx[offset], self.NUMBERS[0][0])

    def test_off_limits_end(self):
        ctx, offset = text.context(self.NUMBERS, 15, 163, width=1)
        self.assertEqual(ctx, "... vierz fünfz")
        self.assertEqual(offset, 10)
        self.assertEqual(ctx[offset], self.NUMBERS[15][0])


if __name__ == '__main__':
    unittest.main()


