"""Defines trends calculations for stations"""
import logging

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


# TODO: Define a Faust Stream that ingests data from the Kafka Connect stations topic and
#   places it into a new topic with only the necessary information.
app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")
# TODO: Define the input Kafka Topic. Hint: What topic did Kafka Connect output to?
topic = app.topic("connector_station", value_type=Station)
# TODO: Define the output Kafka Topic
out_topic = app.topic("station_table", partitions=1)
# TODO: Define a Faust Table
table = app.Table(
    "station_table",
    default=TransformedStation,
    partitions=1,
    changelog_topic=out_topic,
)


#
#
# TODO: Using Faust, transform input `Station` records into `TransformedStation` records. Note that
# "line" is the color of the station. So if the `Station` record has the field `red` set to true,
# then you would set the `line` of the `TransformedStation` record to the string `"red"`
#
#
@app.agent(topic)
async def station(stations):
    async for s in stations:
        if s.red:
            line = "red"
        elif s.blue:
            line = "blue"
        elif s.green:
            line = "green"

        table[s.station_id] = TransformedStation(
            station_id=s.station_id,
            station_name=s.station_name,
            order=s.order,
            line=line
        )


if __name__ == "__main__":
    app.main()
