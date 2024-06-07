#!/bin/bash

spark-submit --master yarn --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 --driver-class-path postgresql-42.6.0.jar --jars postgresql-42.6.0.jar  main.py --mode=$1 --D=$2 --L=$3