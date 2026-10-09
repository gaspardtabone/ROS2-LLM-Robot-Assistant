CREATE TABLE IF NOT EXISTS rooms (
    name TEXT PRIMARY KEY,
    x REAL NOT NULL,
    y REAL NOT NULL,
    yaw REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    room TEXT,
    x REAL NOT NULL,
    y REAL NOT NULL,
    z REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO rooms (name, x, y, yaw) VALUES ('dock', 0.0, 0.0, 0.0);
INSERT OR IGNORE INTO rooms (name, x, y, yaw) VALUES ('living_room', -1.5, 1.0, 0.0);
INSERT OR IGNORE INTO rooms (name, x, y, yaw) VALUES ('kitchen', 2.0, 2.0, 0.0);
INSERT OR IGNORE INTO rooms (name, x, y, yaw) VALUES ('corridor', 0.0, 1.5, 1.57);
