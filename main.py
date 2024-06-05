import socket
import argparse
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_csv, to_timestamp, col, when, date_trunc, sum as _sum, count, window

# Set up argument parsing
parser = argparse.ArgumentParser(description="NYC Yellow Taxi Processing")
parser.add_argument('--mode', type=str, required=True, choices=['A', 'C'], help="Mode: 'A' for real-time with updates, 'C' for real-time with final results only")
args = parser.parse_args()

mode = args.mode

host_name = socket.gethostname()

spark = SparkSession.builder \
    .appName("NYC Yellow Taxi Processing") \
    .getOrCreate()

ds1 = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{host_name}:9092") \
    .option("subscribe", os.getenv("KAFKA_TOPIC_PRODUCER")) \
    .load()

valuesDF = ds1.selectExpr("CAST(value as string)")

schema = "tripID STRING, start_stop INT, timestamp STRING, locationID INT, passenger_count INT, trip_distance DOUBLE, payment_type INT, amount DOUBLE, VendorID STRING"

# Parse the CSV string into columns using the defined schema
parsedDF = valuesDF.select(from_csv(valuesDF.value, schema).alias("data")).select("data.*")

# Convert the timestamp column to a timestamp type if necessary
parsedDF = parsedDF.withColumn("timestamp", to_timestamp("timestamp"))

# Load the static taxi zone lookup data
taxi_zone_lookup = spark.read.csv(os.getenv("TAXI_STATIC_DATA_PATH"), header=True, inferSchema=True)

# Rename the LocationID column for joining purpose
taxi_zone_lookup = taxi_zone_lookup.withColumnRenamed("LocationID", "locationID")

# Join streaming data with static taxi zone lookup data
joinedDF = parsedDF.join(taxi_zone_lookup, "locationID")

# Add a date column for aggregation
joinedDF = joinedDF.withColumn("date", date_trunc("day", "timestamp"))

# Apply watermarking to handle late data, with a delay of 1 day
watermarkedDF = joinedDF.withWatermark("timestamp", "1 day")

# Perform aggregations
aggregatedDF = watermarkedDF.groupBy(
    window(col("timestamp"), "1 day").alias("date"),
    "Borough"
).agg(
    count(when(col("start_stop") == 0, True)).alias("num_departures"),
    count(when(col("start_stop") == 1, True)).alias("num_arrivals"),
    _sum(when(col("start_stop") == 0, col("passenger_count"))).alias("total_departing_passengers"),
    _sum(when(col("start_stop") == 1, col("passenger_count"))).alias("total_arriving_passengers")
)

# Determine output mode based on delay parameter
output_mode = None
if mode == 'A':
    output_mode = "update"
elif mode == 'C':
    output_mode = "append"

# Write the results to the console
query = aggregatedDF.writeStream \
    .outputMode(output_mode) \
    .format("console") \
    .option("truncate", "false") \
    .start()

# Await termination of the query
query.awaitTermination()
