import csv
from datetime import datetime 
from openaq import OpenAQ
import pandas as pd
import sqlite3

#pd.set_option('display.max_columns', None)
def main():
    conn = sqlite3.connect("weather_health.db")
    #with open("schema.sql", "r") as file:
       # schema = file.read()
    #conn.executescript(schema)

    # get API key from .txt file
    file = open("aq_key.txt", "r", encoding="utf-8")
    key = file.read().strip()
    file.close()

    #establish api connection w/ key
    client = OpenAQ(api_key=key)

    a_stations = {"station_name": ["Hawthorne"], "station_id": [288], "api_source": ["OpenAQ"]}
    locations = client.locations.get(a_stations["station_id"][0])
    #print(type(locations))
    #print(locations.results)

    locations_id = locations.results[0].id
    #location_name = locations.results[0].name
    sensors = client.locations.sensors(locations_id)
    #print(locations_id)
    #print(location_name)

    #declare empty array to later append for sensor ids
    sensors_id = []

    #iterate through sensors at given air station and append to array
    for sensor in sensors.results:
        #print(sensor.name, sensor.id)
        sensors_id.append(sensor.id)

    #print(sensors_id)

    #clear aq.csv before re-appending data
    with open("airquality.csv", "w") as csvfile: 
        csvfile.write("")

    #Begin extracting data and writing csv process 
    for id in sensors_id:
        #get access the measurements of the sensors 
        response = client.measurements.list(sensors_id=id,
                                            data="hours",
                                            datetime_from=datetime(2026,1,1,0,0,0),
                                            datetime_to=datetime(2026,2,1,0,0,0)
                                            )

        measurements = response.results


        # Choose column names in .csv output
        headers = ["station_id", "timestamp", "parameter", "unit", "value"]

        # Write each measurement data into .csv
        with open("airquality.csv", "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for item in measurements:
                row = {
                    "station_id": a_stations["station_id"][0],
                    "timestamp": item.period.datetime_to.local,
                    "parameter": item.parameter.name,
                    "unit": item.parameter.units,
                    "value": item.value
                }

                writer.writerow(row)
    # end process 
    client.close()

    #make df from csv 
    df = pd.read_csv("airquality.csv")
    #print(df.shape)
    df = df.drop_duplicates()
    #print(df.shape)

    #duplicates = df[df.duplicated(subset=["timestamp", "parameter"], keep=False)]
    #print(duplicates)

    #pivot df from long to wide
        #give each parameter its own col
    df_wide = df.pivot(
        index=["station_id", "timestamp"], 
        columns="parameter", 
        values="value"
    ).reset_index() #makes station_id and timestamp their own cols

    #drop parameter col (which is NaN)
    df_wide = df_wide.drop(columns=["parameter"])

    #print(df_wide.columns)
    #print(df_wide.head(10))

    #df_wide.to_csv('test.csv', index=False)

    #make a df of station data to append to SQL tab
    stat_df = pd.DataFrame(data=a_stations) 

    #append station data to sql tab
    stat_df.to_sql(
        "stations", #the target table in db 
        conn, 
        if_exists="append", #means take these rows and add them to existsing target tab
        index=False
    )

    #parameters: co, no, no2, nox, o3, pm10, pm25, so2
    #rename the df to airquality_df and rename timestamp to datetime per SQL tab labs 
    airquality_df = df_wide.rename(columns={
        "timestamp": "datetime"
    })

    #print(airquality_df.columns)
    #print(airquality_df.head(10))

    #append data to SQL tab
    airquality_df.to_sql(
        "air_quality", #the target table in db 
        conn, 
        if_exists="append", #means take these rows and add them to existsing 'weather' tab
        index=False
    )

    conn.close()

if __name__ == "__main__":
    main()