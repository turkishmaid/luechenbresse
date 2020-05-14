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
import logging

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
    logging.info(f"sleeping {bubu:0.2f} sec")
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
        logging.info(f"Feed.__init__: {name} ({type}) from {feed}")
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
        logging.info(f"loading module {feed_module_name}")
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
        cnt_no_url = 0
        for raw_entry in fp_feed["entries"]:
            cnt += 1
            entry = self.feed_module.parse_feed_entry(raw_entry)
            if entry[0]: # entry[0]=url         # TODO use named tuple
                unique[entry[0]] = entry
            else:
                cnt_no_url += 1
                logging.info(f"empty URL for '{entry[2]}' dated '{entry[3]}'") # 2=title, 3=ts
        # sort by time
        # TODO list comprehension
        entries = list()
        for url in unique:
            entries.append(unique[url])
        entries.sort(key=lambda tup: tup[3], reverse=True)  # tup[3]=ts
        logging.info(f"{cnt} entries, {cnt_no_url} w/o URL, duplicates removed, remaining: {len(entries)} ")
        return entries

    def get_rss(self):
        logging.info(f"GET {self.name}")
        t0 = time()
        # TODO catch exceptions
        f = feedparser.parse(self.feed)
        #dt = f"{time() - t0:0.3f}s"
        title, published = self.feed_module.parse_feed_header(f["feed"])
        logging.info(f"feed: {title}")
        if published:
            logging.info(f"published: {published}")
        logging.info(f"got from the internet in {time() - t0:0.3f} sec")
        private_connection = False
        if not self.cur:
            private_connection = True
            self._open_db()
        # sort entries by their own timestamps
        entries = self._cleansed_entries(f)
        cnt_new = 0
        cnt_old = 0
        for entry in entries:
            url, rss_id, title, ts = entry
            if self._is_there(url):
                cnt_old += 1
            else:
                cnt_new += 1
                logging.info(f"{ts} {title}")
                self._upsert_article(url, rss_id, title, ts)
        logging.info(f"{cnt_new} new, {cnt_old} known")
        self.conn.commit()
        if private_connection:
            self._close_db()
        logging.info(f"get_rss() total: {time() - t0:0.3f}s")

    def _get_backlog(self):
        private_connection = False
        if not self.cur:
            private_connection = True
            self._open_db()
        # avoid code for removal of the empty URL in the database, can still be done mmanually
        self.cur.execute("""
            SELECT url, ts, title FROM articles
            WHERE ( dl_http != 200 OR dl_http IS NULL ) AND url != ''
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
        logging.info(f"Backlog: {len(a)} Artikel")
        return a

    def _download_article(self, a):
        # a like returned by get_backlog()
        logging.info(f'downloading {a["ts"]} –– {a["title"]}')
        t0 = time()
        try:
            r = requests.get(a["url"])
        except Exception as ex:
            logging.error(ex)
            logging.debug("faking request object")
            r = FakeRequest()
        dt = time() - t0
        logging.info(f'{a["url"]}: {dt:0.3f}s HTTP {r.status_code}')
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
        logging.info(f"Processing backlog for {self.name}")
        backlog = self._get_backlog()
        for i, article in enumerate(backlog):
            logging.info(i)
            self._download_article(article)
            hold_on()


def process_feed(name): # TODO make @staticmethod of Feed
    feed = Feed.from_name(name)
    feed.get_rss()
    feed.process_backlog()

def process_all_feeds(): # TODO make @staticmethod of Feed
    logging.debug("process_all_feeds()")
    feeds = data.feeds()
    logging.debug(f"{len(feeds)} feeds")
    for name in feeds:
        feed = Feed.from_name(name)
        feed.get_rss()
    for name in feeds:
        feed = Feed.from_name(name)
        feed.process_backlog()

if __name__ == "__main__":
    pass