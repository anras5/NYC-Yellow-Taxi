#!/bin/bash

java -cp /usr/lib/kafka/libs/*:./producer/KafkaProducer.jar \
 com.example.bigdata.TestProducer $TAXI_STREAM_DATA_PATH 15 $KAFKA_TOPIC_PRODUCER 1 ${CLUSTER_NAME}-w-0:9092
