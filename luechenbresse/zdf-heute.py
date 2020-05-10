#!/usr/bin/env python
# coding: utf-8

"""
Special coding for the zdf-heute RSS feed.
We can re-think the exit-mechanism later (class/interface, whatever...).

Created: 09.05.20
"""

from datetime import datetime
from time import mktime

def parse_feed_header(feed_header):
    return feed_header["title"], feed_header["published"]

def parse_feed_entry(feed_entry):
    url = feed_entry["link"]
    rss_id = feed_entry["id"]
    title = feed_entry["title"]
    ts = datetime.fromtimestamp(mktime(feed_entry["published_parsed"])).isoformat()
    return url, rss_id, title, ts


if __name__ == "__main__":
    pass