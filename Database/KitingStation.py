from neo4j import GraphDatabase

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+s://22b74052.databases.neo4j.io"
AUTH = ("neo4j", "VpjLxlIwDhXj1nzSD2R8VZbELCreCkVCZG_N6kuBCOk")

import logging

from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import DriverError, Neo4jError
import logging

class KitingDatabase:

    def __init__(self, database=None):
        self.driver = GraphDatabase.driver(uri=URI, auth=AUTH)
        self.database = database

    def close(self):
        self.driver.close()

    # Method to create a new station or update its information
    def create_station(self, name, latitude, longitude, altitude=None, 
                       region=None, country=None, timezone=None, 
                       is_coastal=False, water_type=None, 
                       active_since=None, data_update_frequency=None):
        with self.driver.session() as session:
            session.execute_write(
                self._create_station, name, latitude, longitude, altitude,
                region, country, timezone, is_coastal, water_type,
                active_since, data_update_frequency, 1
            )
            print(f"Station {name} created or updated successfully.")

    @staticmethod
    def _create_station(tx, name, latitude, longitude, altitude,
                        region, country, timezone, is_coastal, water_type,
                        active_since, data_update_frequency, station_id=None):
        query = """
        MERGE (station:KitingStation {name: $name})
        SET station.latitude = $latitude,
            station.longitude = $longitude,
            station.altitude = $altitude,
            station.region = $region,
            station.country = $country,
            station.timezone = $timezone,
            station.is_coastal = $is_coastal,
            station.water_type = $water_type,
            station.active_since = $active_since,
            station.data_update_frequency = $data_update_frequency
        """
        try:
            tx.run(query, station_id=station_id, name=name, latitude=latitude,
                   longitude=longitude, altitude=altitude, region=region,
                   country=country, timezone=timezone, is_coastal=is_coastal,
                   water_type=water_type, active_since=active_since,
                   data_update_frequency=data_update_frequency)
        except (DriverError, Neo4jError) as exception:
            logging.error("Error creating station: %s", exception)
            raise

    # Method to retrieve station information
    def get_station(self, station_id):
        with self.driver.session() as session:
            result = session.execute_read(
                self._fetch_station,
                station_id
            )
            return result

    @staticmethod
    def _fetch_station(tx, station_id):
        query = """
        MATCH (station:KitingStation {station_id: $station_id})
        RETURN station.station_id AS station_id,
               station.name AS name,
               station.location AS location
        """
        result = tx.run(query, station_id=station_id)
        record = result.single()
        if record:
            return {
                "station_id": record["station_id"],
                "name": record["name"],
                "location": record["location"]
            }
        else:
            return None

    # Method to add daily wind data
    def add_daily_wind_data(self, station_id, year, month, day, hourly_timestamps, average_speeds, gusts, directions):
        with self.driver.session() as session:
            session.execute_write(
                self._create_daily_wind_data,
                station_id, year, month, day, hourly_timestamps, average_speeds, gusts, directions
            )
            print(f"Stored wind data for station {station_id} on {year}-{month}-{day}")

    @staticmethod
    def _create_daily_wind_data(tx, station_id, year, month, day, hourly_timestamps, average_speeds, gusts, directions):
        query = """
        MERGE (station:KitingStation {station_id: $station_id})
        MERGE (station)-[:HAS_DATA]->(y:Year {year: $year})
        MERGE (y)-[:IN_MONTH]->(m:Month {month: $month})
        MERGE (m)-[:IN_DAY]->(d:Day {day: $day})
        MERGE (d)-[:HAS_WIND_DATA]->(w:WindData)
        SET w.hourly_timestamps = $hourly_timestamps,
            w.average_speeds = $average_speeds,
            w.gusts = $gusts,
            w.directions = $directions
        """

        try:
            tx.run(query, station_id=station_id, year=year, month=month, day=day,
                   hourly_timestamps=hourly_timestamps, average_speeds=average_speeds,
                   gusts=gusts, directions=directions)
        except (DriverError, Neo4jError) as exception:
            logging.error("Error storing wind data: %s", exception)
            raise

    # Method to retrieve daily wind data
    def get_daily_wind_data(self, station_id, year, month, day):
        with self.driver.session() as session:
            result = session.execute_read(
                self._fetch_daily_wind_data,
                station_id, year, month, day
            )
            return result

    @staticmethod
    def _fetch_daily_wind_data(tx, station_id, year, month, day):
        query = """
        MATCH (station:KitingStation {station_id: $station_id})-[:HAS_DATA]->(y:Year {year: $year})-[:IN_MONTH]->(m:Month {month: $month})-[:IN_DAY]->(d:Day {day: $day})-[:HAS_WIND_DATA]->(w:WindData)
        RETURN w.hourly_timestamps AS hourly_timestamps,
               w.average_speeds AS average_speeds,
               w.gusts AS gusts,
               w.directions AS directions
        """

        result = tx.run(query, station_id=station_id, year=year, month=month, day=day)
        record = result.single()
        if record:
            return {
                "hourly_timestamps": record["hourly_timestamps"],
                "average_speeds": record["average_speeds"],
                "gusts": record["gusts"],
                "directions": record["directions"]
            }
        else:
            return None

# Usage example
if __name__ == "__main__":
    # Connect to the database
    db = KitingDatabase(uri="neo4j+s://22b74052.databases.neo4j.io", user="neo4j", password="your_password")

    # Add a new station
    station_id = "123"
    name = "Windy Cove"
    location = "Coordinates or address here"
    db.create_station(station_id, name, location)

    # Retrieve station information
    station_info = db.get_station(station_id)
    print("Station Information:", station_info)

    # Example data for January 10, 2024, at the station
    year = 2024
    month = 1
    day = 10
    hourly_timestamps = ["2024-01-10T00:00", "2024-01-10T01:00", "2024-01-10T02:00"]
    average_speeds = [10, 12, 15]
    gusts = [20, 25, 30]
    directions = [270, 280, 260]

    # Add daily wind data
    db.add_daily_wind_data(station_id, year, month, day, hourly_timestamps, average_speeds, gusts, directions)

    # Retrieve daily wind data
    wind_data = db.get_daily_wind_data(station_id, year, month, day)
    print("Retrieved Wind Data:", wind_data)

    # Close the database connection
    db.close()


