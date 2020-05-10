#!/usr/bin/env python
# coding: utf-8

"""
Cares for downloading the feed and the references articles.

Created: 09.05.20
"""

import json
from time import time, mktime, sleep
from datetime import datetime
import random
import sqlite3
from pathlib import Path
import importlib

import requests
import feedparser

from luechenbresse import ini
from luechenbresse import data


# mimicks a very simple Request object when a request failed
class FakeRequest:
    def __init__(self):
        self.status_code = 999
        self.text = "Hurz."


# tame network requests
def hold_on():
    bubu = random.uniform(3, 8)
    print(f"sleeping {bubu:0.2f} sec")
    sleep(bubu)


class Feed:

    @staticmethod
    def from_json(name, feed):
        return Feed(name, feed["feed"], feed["type"], feed["db"], feed["type"])

    @staticmethod
    def from_name(name):
        feed_list = data.feeds()
        feed = feed_list[name]
        return Feed.from_json(name, feed)

    def __init__(self, name, feed, type, db, schema):
        """
        Constructor.
        :param feed: url of the feed
        :param type: rss|...
        :param db: name of the db file (location from luechenbresse.ini)
        :param schema: list(str) of schemas to apply
        """
        self.name = name
        self.feed = feed
        self.type = type
        ini_path = ini.get("databases", "folder")
        if not ini_path:
            raise ValueError(f"No database folder specified in luechenbresse.ini")
        ini_file = Path(ini_path)
        self.db = ini_file / db
        self.schema = schema # TODO support more than one schema
        feed_module_name = "luechenbresse."+name
        print(f"loading module {feed_module_name}")
        self.feed_module = importlib.import_module(feed_module_name)
        # methods will open and close connection if not done from outside
        self.conn = None
        self.cur = None

    def _open_db(self):
        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()

    def _close_db(self):
        self.conn.close()
        self.conn = None
        self.cur = None

    def _is_there(self, url):
        sql = """
            SELECT * 
            FROM articles 
            WHERE url = ?
        """
        rows = [r for r in self.cur.execute(sql, (url,))]
        return len(rows) == 1

    def _upsert_article(self, url, rss_id, title, ts):
        sql = """
            INSERT INTO articles(url, rss_id, title, ts, realised_ts) 
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT DO NOTHING
        """
        now = datetime.now().isoformat()[:19]
        row_tbi = (url, rss_id, title, ts, now)
        self.cur.execute(sql, row_tbi)

    def _cleansed_entries(self, fp_feed):
        # remove duplicates
        unique = dict()
        cnt = 0
        for raw_entry in fp_feed["entries"]:
            cnt += 1
            entry = self.feed_module.parse_feed_entry(raw_entry)
            unique[entry[0]] = entry
        # sort by time
        # TODO list comprehension
        entries = list()
        for url in unique:
            entries.append(unique[url])
        entries.sort(key=lambda tup: tup[3], reverse=True)  # tup[3]=ts
        return entries, cnt - len(entries)

    def get_rss(self):
        t0 = time()
        # TODO catch exceptions
        f = feedparser.parse(self.feed)
        #dt = f"{time() - t0:0.3f}s"
        title, published = self.feed_module.parse_feed_header(f["feed"])
        print("feed:", title)
        if published:
            print("published:", published)
        print(f"got from the internet in {time() - t0:0.3f} sec")
        private_connection = False
        if not self.cur:
            private_connection = True
            self._open_db()
        # sort entries by their own timestamps
        entries, cnt_dup = self._cleansed_entries(f)
        cnt_new = 0
        cnt_old = 0
        for entry in entries:
            url, rss_id, title, ts = entry
            if self._is_there(url):
                cnt_old += 1
            else:
                cnt_new += 1
                print(ts, title)
                self._upsert_article(url, rss_id, title, ts)
        print(f"{cnt_new} new, {cnt_old} known, {cnt_dup} duplicates ignored")
        self.conn.commit()
        if private_connection:
            self._close_db()
        dt = f"{time() - t0:0.3f}s"
        print(dt)

    def _get_backlog(self):
        private_connection = False
        if not self.cur:
            private_connection = True
            self._open_db()
        self.cur.execute("""
            SELECT url, ts, title FROM articles
            WHERE dl_http != 200 OR dl_http IS NULL
            ORDER BY ts
        """)
        rows = self.cur.fetchall()
        if private_connection:
            self._close_db()
        a = list()
        for row in rows:
            a.append({
                "url": row[0],
                "ts": row[1],
                "title": row[2]
            })
        print(f"Backlog: {len(a)} Artikel")
        return a

    def _download_article(self, a):
        # a like returned by get_backlog()
        print(f'{a["ts"]} –– {a["title"]}')
        t0 = time()
        try:
            r = requests.get(a["url"])
        except Exception as ex:
            print(ex)
            r = FakeRequest()
        dt = time() - t0
        print(f'{a["url"]}: {dt:0.3f}s HTTP {r.status_code}')
        text = r.text if r.status_code == 200 else None
        now = datetime.now().isoformat()[:19]
        row = (now, r.status_code, dt, text, a["url"])
        private_connection = False
        if not self.cur:
            private_connection = True
            self._open_db()
        self.cur.execute("""
            UPDATE articles
            SET dl_ts = ?, dl_http = ?, dl_dt = ?, html = ?
            WHERE url = ?
        """, row)
        self.conn.commit()
        if private_connection:
            self._close_db()

    def process_backlog(self):
        backlog = self._get_backlog()
        for i, article in enumerate(backlog):
            print()
            print(i)
            self._download_article(article)
            hold_on()


def header(s):
    print()
    print()
    print(s)
    print()

def process_feed(name):
    feed = Feed.from_name(name)
    header("Get RSS Feed...")
    feed.get_rss()
    header("Download New Articles...")
    feed.process_backlog()
    header("Ciao.")

def process_all_feeds():
    feeds = data.feeds()
    for name in feeds:
        feed = Feed.from_name(name)
        header(f"Get RSS Feed {name}...")
        feed.get_rss()
    for name in feeds:
        feed = Feed.from_name(name)
        header(f"Download New Articles For {name}...")
        feed.process_backlog()
    header("Ciao.")


if __name__ == "__main__":
    pass