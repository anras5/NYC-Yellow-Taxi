#!/bin/bash

if [ "$1" == "up" ]; then
    echo "Tworzenie tematów Kafki..."
    kafka-topics.sh --bootstrap-server ${CLUSTER_NAME}-w-1:9092 --create --replication-factor 1 --partitions 1 --topic $KAFKA_TOPIC_PRODUCER
elif [ "$1" == "down" ]; then
    echo "Usuwanie tematów Kafki..."
    kafka-topics.sh --bootstrap-server ${CLUSTER_NAME}-w-1:9092 --delete --topic $KAFKA_TOPIC_PRODUCER
elif [ "$1" == "show" ]; then
    echo "Dostępne tematy Kafki:"
    kafka-topics.sh --bootstrap-server ${CLUSTER_NAME}-w-1:9092 --list
else
    echo "Użycie: $0 {up|down|show}"
    exit 1
fi

echo "Done!"