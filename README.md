# NYC-Yellow-Taxi + Spark

1. Producent i skrypty inicjujące i zasilające

- Utwórz klaster na platformie GCP przy użyciu poniższego polecenia
```shell
gcloud dataproc clusters create ${CLUSTER_NAME} \
--enable-component-gateway --bucket ${BUCKET_NAME} \
--region ${REGION} --subnet default \
--master-machine-type n1-standard-4 --master-boot-disk-size 50 \
--num-workers 2 --worker-machine-type n1-standard-2 --worker-boot-disk-size 50 \
--image-version 2.1-debian11 --optional-components FLINK,DOCKER,ZOOKEEPER \
--project ${PROJECT_ID} --max-age=3h \
--metadata "run-on-master=true" \
--initialization-actions \
gs://goog-dataproc-initialization-actions-${REGION}/kafka/kafka.sh
```

- Otwórz terminal SSH do maszyny master i wgraj na nią pliki z projektu.

- Uruchom skrypt inicjalizujący środowisko. Pobiera on niezbędne biblioteki, dane wejściowe do projektu
oraz ustawia zmienne środowiskowe (dlatego uruchamiamy poprzez polecenie source).
Skrypt przyjmuje dwa parametry: pierwszy to folder w usłudze Cloud Storage,
w którym znajdują się pliki główne (strumieniowe - zbiór pierwszy),
a drugi to lokalizacja pliku statycznego (zbiór drugi) w usłudze Cloud Storage.

```shell
source setup.sh <pathToYellowTripDataResult> <pathToTaxiZoneLookup>
```
Przykładowo:
```shell
source setup.sh gs://pbd-23-AA/projekt2/yellow_tripdata_result gs://pbd-23-AA/projekt2/taxi_zone_lookup.csv
```

- Uruchom skrypt tworzący tematy źródłowe Kafki.
```shell
./manage-topics.sh up
```

- Uruchom skrypt tworzący ujście dla przetwarzania ETL.
```shell
./run-sink.sh
```

- Uruchom skrypt zasilający temat Kafki. 
```shell
./run-producer.sh
```