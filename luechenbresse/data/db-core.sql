-- noinspection SqlNoDataSourceInspectionForFile

-- raw data from the internet
CREATE TABLE IF NOT EXISTS articles (
    -- from feed or archive
    url TEXT PRIMARY KEY,       -- referenced URL, assuming this is not reused later
                                -- TODO: make sure that older articles with http 200 will not be overwritten
                                --          by batch runs, only by manual fixes
    rss_id TEXT,                -- id-field from RSS feed
    title TEXT,                 -- decorative only, can be used for console output
    ts TEXT,                    -- iso timestamp of data
    realised_ts TEXT,           -- iso timestamp when the article was recognized by the feed reader
    -- from referenced URLs, start life as NULL
    dl_ts TEXT,                 -- iso timestamp download
    dl_http INT,                -- HTTP status code of download
    dl_dt REAL,                 -- response time of the GET request
    html TEXT                   -- raw HTML as downloaded from the internet
);

-- cooked data, reproducible from raw data above
CREATE TABLE IF NOT EXISTS parsed (
    -- raw data
    url TEXT PRIMARY KEY,       -- foreign key to articles
    ts TEXT,                    -- iso timestamp of data
    -- parsed data
    text_json TEXT,             -- as parsed from HTML, with punctuation and structure
                                --      use as json.loads(text_json)
    meta_json TEXT,
    plain TEXT,                 -- tokenited, no punctuation
                                --      use as plain.split()
    calweek TEXT,               -- like 2020.53
    dow TEXT,                   -- like 'Mo', 'Di', ...
    -- parser meta
    parser INTEGER              -- parser version, use to apply new parser versions to already parsed data
);

-- counting words occurrences per week, normalized terms
CREATE TABLE IF NOT EXISTS words_by_week (
    word TEXT,                  -- somehow normalized
    calweek TEXT,               -- like 2020.53
    cnt_occ INTEGER,            -- count word occurrences
    cnt_art INTEGER,            -- count articles where the word occurs
    PRIMARY KEY(word, calweek)
);
