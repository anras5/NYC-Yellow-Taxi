#!/bin/bash

spark-submit --master yarn --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 main.py --mode=C