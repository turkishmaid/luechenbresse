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
        sql1 = data.schema(schema)
        self.assertIn("CREATE TABLE", sql1)


if __name__ == '__main__':
    unittest.main()
