import argparse
import os
import socket

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, from_csv, sum as _sum, to_timestamp, when, window, coalesce, \
    lit

parser = argparse.ArgumentParser(description="NYC Yellow Taxi Processing")
parser.add_argument('--mode', type=str, required=True, choices=['A', 'C'],
                    help="Mode: 'A' for real-time with updates, 'C' for real-time with final results only")
parser.add_argument('--D', type=int, required=True, help="Time window length in hours for anomaly detection")
parser.add_argument('--L', type=int, required=True, help="Minimum number of people for anomaly detection")
args = parser.parse_args()

mode = args.mode
D = args.D
L = args.L

host_name = socket.gethostname()

spark = SparkSession.builder \
    .appName("NYC Yellow Taxi Processing") \
    .getOrCreate()

# -------------------------------------------------------------------------------------------------------------------- #
# STREAM
ds1 = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{host_name}:9092") \
    .option("subscribe", os.getenv("KAFKA_TOPIC_PRODUCER")) \
    .load()
valuesDF = ds1.selectExpr("CAST(value as string)")
schema = "tripID STRING, start_stop INT, timestamp STRING, locationID INT, passenger_count INT, trip_distance DOUBLE," \
         " payment_type INT, amount DOUBLE, VendorID STRING"
parsedDF = valuesDF.select(from_csv(valuesDF.value, schema).alias("data")).select("data.*")
parsedDF = parsedDF.withColumn("timestamp", to_timestamp("timestamp"))

# -------------------------------------------------------------------------------------------------------------------- #
# STATIC
taxi_zone_lookup = spark.read.csv(os.getenv("TAXI_STATIC_DATA_PATH"), header=True, inferSchema=True)
taxi_zone_lookup = taxi_zone_lookup.withColumnRenamed("LocationID", "locationID")

# -------------------------------------------------------------------------------------------------------------------- #
# JOIN
joinedDF = parsedDF.join(taxi_zone_lookup, "locationID")

# -------------------------------------------------------------------------------------------------------------------- #
# WATERMARK
watermarkedDF = joinedDF.withWatermark("timestamp", "1 day")

# -------------------------------------------------------------------------------------------------------------------- #
# ETL

# AGREGACJE
aggregatedDF = watermarkedDF.groupBy(
    window(col("timestamp"), "1 day").alias("date"),
    "Borough"
).agg(
    coalesce(count(when(col("start_stop") == 0, True)), lit(0)).alias("num_departures"),
    coalesce(count(when(col("start_stop") == 1, True)), lit(0)).alias("num_arrivals"),
    coalesce(_sum(when(col("start_stop") == 0, col("passenger_count"))), lit(0)).alias("total_departing_passengers"),
    coalesce(_sum(when(col("start_stop") == 1, col("passenger_count"))), lit(0)).alias("total_arriving_passengers")
)

# UJŚCIE ETL
output_mode = None
if mode == 'A':
    output_mode = "update"
elif mode == 'C':
    output_mode = "append"

query_etl = aggregatedDF.writeStream.outputMode(output_mode).foreachBatch(
    lambda df_batch, batch_id:
    df_batch.select(
        col("date").cast("string").alias("day"),
        col("Borough").alias("borough"),
        col("num_departures"),
        col("num_arrivals"),
        col("total_departing_passengers"),
        col("total_arriving_passengers")
    ).write
    .format("jdbc")
    .mode("append")
    .option("url", f"jdbc:postgresql://{host_name}:54320/streamoutput")
    .option("dbtable", "taxi_etl")
    .option("user", "postgres")
    .option("password", os.getenv("PGPASSWORD"))
    .save()
).option("checkpointLocation", "/tmp/etl").start()

# -------------------------------------------------------------------------------------------------------------------- #
# ANOMALY

# AGREGACJE
anomalyDF = watermarkedDF.groupBy(
    window(col("timestamp"), f"1 day").alias("anomaly_window"),
    "Borough"
).agg(
    coalesce(_sum(when(col("start_stop") == 0, col("passenger_count"))), lit(0)).alias("total_departing_passengers"),
    coalesce(_sum(when(col("start_stop") == 1, col("passenger_count"))), lit(0)).alias("total_arriving_passengers")
).withColumn(
    "difference", col("total_departing_passengers") - col("total_arriving_passengers")
).filter(
    col("difference") >= L
)

query_anomaly = anomalyDF.selectExpr(
    "anomaly_window",
    "Borough AS borough",
    "total_departing_passengers",
    "total_arriving_passengers",
    "difference"
).selectExpr(
    "to_json(struct(*)) AS value"
).writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{host_name}:9092") \
    .option("topic", os.getenv("KAFKA_TOPIC_ANOMALIES")) \
    .option("checkpointLocation", "/tmp/anomalies") \
    .start()

# .trigger(processingTime="1 hour") \

spark.streams.awaitAnyTermination()
