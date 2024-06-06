#!/bin/bash

docker run -p 54320:5432 -e POSTGRES_PASSWORD="${PGPASSWORD}" -v "$(pwd)/create_tables.sql:/docker-entrypoint-initdb.d/create_tables.sql" --name postgresik -d postgres