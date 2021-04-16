CREATE TABLE IF NOT EXISTS gitrepo (
    id          VARCHAR(16) PRIMARY KEY NOT NULL,
    name        VARCHAR(125),
    full_name   VARCHAR(125),
    size        INTEGER DEFAULT 0,
    stargazers_count     INTEGER DEFAULT 0,
    watchers_count     INTEGER DEFAULT 0,
    timestamp   datetime NOT NULL
);
