import pandas as pd
import requests
import sqlite3

#pd.set_option('display.max_columns', None)
def main():
#eventually there needs to be only one script that calls the sql schema to build the tables
#if both weather and air scripts call it they will overwrite eachother. 
    conn = sqlite3.connect("weather_health.db")
    #with open("schema.sql", "r") as file:
        #schema = file.read()
    #conn.executescript(schema)

    #declare dicts of weather stations 
    w_stations = {"station_name": ["Salt Lake City Internat'l Airport"],  "station_id": ["USW00024127"], "api_source": ["NCEI"]}

    #delcare dict of parameters 
    #for weather, we are using temperature, humidity, precipitation, and weather type
    w_dataTypes = {"NCEI": ["HourlyDryBulbTemperature,HourlyRelativeHumidity,HourlyPrecipitation,HourlyPresentWeatherType"]}

    def check_save(response, filename):
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"{filename} CSV downloaded successfully!")
        else:
            print(f"{filename} download failed.")

    #ISO Date Time format is YYYY-MM-DD or YYYY-MM-DDTHH:MM:ss"
    def api_req_weather(mode, datatypes, stations, start, end, format):
        """request data via API at a given date time interval, for a weather station in the US, 
        mode is past data or forecast data. datatypes are temp, 
        relative humidity, dew point etc. Dataset is Local Climatology Data from NCEI for past data. 
        """
        if mode == "past":
            base = "https://www.ncei.noaa.gov/access/services/data/v1?dataset=local-climatological-data-v2"
        elif mode == "fore": 
            pass

        options = {}
        options["url"] = base
        options["datatypes"] = datatypes
        options["stations"] = stations
        options["start"] = start
        options["end"] = end
        options["format"] = format

        #multple parameters i.e. dataTypes can be passed. 
        url = options["url"] + \
            "&dataTypes=" + options["datatypes"] + \
                "&stations=" + options["stations"] + \
                "&startDate=" + options["start"] + \
                "&endDate=" + options["end"] + \
                "&format=" + options["format"]
        #print(url)
        response = requests.get(url=url)
        return response

    #print(w_stations["station_id"][0])

    w_response = api_req_weather(mode="past",
                                    datatypes=w_dataTypes["NCEI"][0],
                                    stations=w_stations["station_id"][0],
                                    start="2026-01-01",
                                    end="2026-02-01",
                                    format="csv")

    #check if api call is successful, then save as csv
    check_save(w_response, "weather.csv")

    df = pd.read_csv("weather.csv")

    stat_df = pd.DataFrame(data=w_stations) 

    stat_df.to_sql(
        "stations", #the target table in db 
        conn, 
        if_exists="append", #means take these rows and add them to existsing 'weather' tab
        index=False
    )

    weather_df = df[[
        "STATION",
        "DATE",
        "HourlyDryBulbTemperature",
        "HourlyRelativeHumidity",
        "HourlyPrecipitation"
    ]]

    weather_df = weather_df.rename(columns={
        "STATION": "station_id",
        "DATE": "datetime",
        "HourlyDryBulbTemperature": "temperature",
        "HourlyRelativeHumidity": "humidity",
        "HourlyPrecipitation": "precipitation"
    })

    #print(weather_df.columns)
    #print(weather_df.head())

    weather_df.to_sql(
        "weather", #the target table in db 
        conn, 
        if_exists="append", #means take these rows and add them to existsing 'weather' tab
        index=False
    )

    conn.close()

if __name__ == "__main__":
    main()