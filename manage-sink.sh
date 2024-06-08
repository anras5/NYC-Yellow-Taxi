#!/bin/bash

if [ "$1" == "up" ]; then
    echo "Tworzenie ujścia ETL..."
    docker run -p 54320:5432 -e POSTGRES_PASSWORD="${PGPASSWORD}" -v "$(pwd)/create_tables.sql:/docker-entrypoint-initdb.d/create_tables.sql" --name postgresik -d postgres
elif [ "$1" == "down" ]; then
    echo "Usuwanie ujścia ETL..."
    docker container rm -f postgresik
else
    echo "Użycie: $0 {up|down}"
    exit 1
fi

echo "Done!"