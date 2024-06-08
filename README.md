# NYC-Yellow-Taxi + Spark

# Spis treści:
1. Opis zadania
2. Producent; skrypty inicjujące i zasilający

# Zadania:

### ETL – obraz czasu rzeczywistego
Utrzymywanie agregacji na poziomie dnia i dzielnicy.
Wartości agregatów to:
- liczba wyjazdów
- liczba przyjazdów
- sumaryczna osób wyjeżdżających
- sumaryczna osób przyjeżdżających 

### Wykrywanie "anomalii"
Wykrywanie "anomalii" ma polegać na wykrywaniu dużej różnicy w liczbie osób wyjeżdżających z danej dzielnicy w
stosunku do liczby przyjeżdżających do danej dzielnicy w określonym czasie.
Program ma być parametryzowany przez: 
- D - długość okresu czasu wyrażoną w godzinach
- L - liczbę osób (minimalna)

Wykrywanie anomalii ma być dokonywane co godzinę. \
Przykładowo, dla parametrów D=4, L=10000 program co godzinę będzie raportował te dzielnice, w których w ciągu
ostatnich 4 godzin liczba osób "zmniejszyła się" o co najmniej 10 tysięcy osób.
Raportowane dane mają zawierać:
- analizowany okres - okno (start i stop)
- nazwę dzielnicy
- liczbę osób wyjeżdżających
- liczbę osób przyjeżdżających
- różnicę w powyższych liczbach

# Producent i skrypty inicjujące i zasilające

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

- Otwórz terminal SSH do maszyny master i wgraj na nią pliki z projektu:
    - setup.sh
    - manage-topics.sh
    - run-sink.sh (create_tables.sql)
    - run-processing.sh (main.py)
    - run-producer.sh (KafkaProducer.jar)

- Skrypt inicjalizujący środowisko. Pobiera on niezbędne biblioteki, dane wejściowe do projektu
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

- Skrypt tworzący tematy Kafki (źródłowy temat oraz temat dla anomalii).

```shell
./manage-topics.sh <up|down>
```

## Utrzymanie obrazu czasu rzeczywistego.


- Skrypt przetwarzający dane w wersji A

```shell
./run-processing.sh A 10 5
```

- Uruchom skrypt przetwarzający dane w wersji C

```shell
./run-processing.sh C 10 5
```

- Uruchom skrypt zasilający temat Kafki.

```shell
./run-producer.sh
```