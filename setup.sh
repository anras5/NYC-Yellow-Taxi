#!/bin/bash

# Funkcja ustawia zmienną środowiskową w pliku .bashrc o ile już taka nie istnieje
add_to_bashrc() {
    local var_name="$1"
    local var_value="$2"

    if ! grep -q "^export $var_name=" ~/.bashrc; then
        echo "export $var_name=$var_value" >> ~/.bashrc
        echo "Dodano $var_name do .bashrc"
    else
        echo "$var_name już istnieje w pliku .bashrc, nie dodaję"
    fi
}

# Ustawienia zmiennych środowiskowych
CLUSTER_NAME=$(/usr/share/google/get_metadata_value attributes/dataproc-cluster-name)
TAXI_STREAM_DATA_PATH="${HOME}/data/yellow_tripdata_result"
TAXI_STATIC_DATA_PATH="${HOME}/data/taxi_zone_lookup.csv"

KAFKA_TOPIC_PRODUCER="producer"

add_to_bashrc "CLUSTER_NAME" "$CLUSTER_NAME"
add_to_bashrc "TAXI_STREAM_DATA_PATH" "$TAXI_STREAM_DATA_PATH"
add_to_bashrc "TAXI_STATIC_DATA_PATH" "$TAXI_STATIC_DATA_PATH"
add_to_bashrc "KAFKA_TOPIC_PRODUCER" "$KAFKA_TOPIC_PRODUCER"

source ~/.bashrc

echo "Tworzenie folderu data"
[ -d "${HOME}/data" ] || mkdir "${HOME}/data"

echo "Kopiowanie pliku statycznego z usługi Cloud Storage..."
hadoop fs -copyToLocal $1 "${TAXI_STATIC_DATA_PATH}"

echo "Kopiowanie plików strumieniowych z usługi Cloud Storage..."
hadoop fs -copyToLocal $2 "${TAXI_STREAM_DATA_PATH}"

echo "Ustawianie uprawnień dla skryptów z projektu..."
chmod +x $(pwd)/*.sh

echo "Done!"