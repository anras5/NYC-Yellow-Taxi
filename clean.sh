#!/bin/bash

echo "Usuwanie ujścia ETL..."
docker container rm -f postgresik

echo "Usuwanie tematów Kafki..."
kafka-topics.sh --bootstrap-server ${CLUSTER_NAME}-w-1:9092 --delete --topic $KAFKA_TOPIC_PRODUCER
kafka-topics.sh --bootstrap-server ${CLUSTER_NAME}-w-1:9092 --delete --topic $KAFKA_TOPIC_ANOMALIES

echo "Usuwanie checkpointów Sparka..."
hdfs dfs -rm -r "/tmp/etl" && hdfs dfs -rm -r "/tmp/anomalies"

