import airquality
import sqlite3
import weather

#establish connection with SQL db
    #and execute the schema to build the tables
conn = sqlite3.connect("weather_health.db")     
with open("schema.sql", "r") as file:
    schema = file.read()
conn.executescript(schema)

conn.close()

# connect to and extract weather data via NCEI API
weather.main()

# connect to and extract air quality data via OpenAQ API
airquality.main()