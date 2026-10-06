DROP TABLE IF EXISTS stations; 

CREATE TABLE IF NOT EXISTS stations (
    station_id TEXT PRIMARY KEY,
    station_name TEXT, 
    api_source TEXT
);

DROP TABLE IF EXISTS weather; 

CREATE TABLE IF NOT EXISTS weather (
    weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT,
    datetime TEXT,
    temperature REAL,
    humidity REAL,
    precipitation REAL,
    weather_type TEXT, 

    FOREIGN KEY(station_id)
        REFERENCES stations(station_id)
);

DROP TABLE IF EXISTS air_quality; 

CREATE TABLE IF NOT EXISTS air_quality (
    air_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT,
    datetime TEXT,
    co REAL,
    no REAL,
    no2 REAL,
    nox REAL,
    o3 REAL,
    pm10 REAL,
    pm25 REAL,
    so2 REAL,

    FOREIGN KEY(station_id)
        REFERENCES stations(station_id)
);