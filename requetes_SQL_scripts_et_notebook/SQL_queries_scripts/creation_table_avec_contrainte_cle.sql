CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    fatherId INTEGER,
    motherId INTEGER,
    age INTEGER,
    FOREIGN KEY (fatherId) REFERENCES people(id),
    FOREIGN KEY (motherId) REFERENCES people(id)
);