#!/usr/bin/env python
# coding: utf-8

import unittest
from luechenbresse import data


class TestData(unittest.TestCase):

    def test_reads_feed_list(self):
        feeds = data.json("feeds.json")
        self.assertTrue(isinstance(feeds, dict))
        self.assertTrue("zdf-heute" in feeds)
        self.assertTrue("type" in feeds["zdf-heute"])
        self.assertEqual(feeds["zdf-heute"]["type"], "rss")

    def test_schema(self):
        schema = "db-core.sql"
        sql1, from_buffer = data.schema(schema)
        self.assertFalse(from_buffer)           # TODO? may fail when other test already reads that
        self.assertIn("CREATE TABLE", sql1)
        sql2, from_buffer = data.schema(schema)
        self.assertTrue(from_buffer)
        self.assertEqual(sql2, sql1)


if __name__ == '__main__':
    unittest.main()
