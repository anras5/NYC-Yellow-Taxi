#!/bin/bash

add_to_bashrc() {
    local var_name="$1"
    local var_value="$2"

    sed -i "/^export $var_name=/d" ~/.bashrc

    echo "export $var_name=$var_value" >> ~/.bashrc
    echo "Dodano $var_name do .bashrc"
}

# Ustawienia zmiennych środowiskowych
CLUSTER_NAME=$(/usr/share/google/get_metadata_value attributes/dataproc-cluster-name)
TAXI_STREAM_DATA_PATH="${HOME}/data/yellow_tripdata_result"
TAXI_STATIC_DATA_PATH="${HOME}/data/taxi_zone_lookup.csv"

KAFKA_TOPIC_PRODUCER="producer"

POSTGRES_PASSWORD="bigdatapassword123"

add_to_bashrc "CLUSTER_NAME" "$CLUSTER_NAME"
add_to_bashrc "TAXI_STREAM_DATA_PATH" "$TAXI_STREAM_DATA_PATH"
add_to_bashrc "TAXI_STATIC_DATA_PATH" "$TAXI_STATIC_DATA_PATH"
add_to_bashrc "KAFKA_TOPIC_PRODUCER" "$KAFKA_TOPIC_PRODUCER"

source ~/.bashrc

echo "Tworzenie folderu data"
[ -d "${HOME}/data" ] || mkdir "${HOME}/data"

echo "Kopiowanie plików strumieniowych z usługi Cloud Storage..."
hadoop fs -copyToLocal $1 "${TAXI_STREAM_DATA_PATH}"

echo "Kopiowanie pliku statycznego z usługi Cloud Storage..."
hadoop fs -copyToLocal $2 "${TAXI_STATIC_DATA_PATH}"

echo "Ustawianie uprawnień dla skryptów z projektu..."
chmod +x $(pwd)/*.sh

echo "Done!"