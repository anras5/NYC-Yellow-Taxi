#!/bin/bash

psql -h localhost -p 54320 -U postgres -d streamoutput -c "SELECT * FROM taxi_etl;"