# Kafka Generator

This script is used in conjuction with the `kafka-request-generator` application to generate random Kafka
requests and responses.

## Usage

```text
usage: kafka-generator.py [-h] -d SCHEMATA_DIR -g KAFKA_REQ_GEN
                          --request-output-dir REQUEST_OUTPUT_DIR
                          --response-output-dir RESPONSE_OUTPUT_DIR

Kafka Protocol Parser Generator

options:
  -h, --help            show this help message and exit
  -d SCHEMATA_DIR, --schemata-dir SCHEMATA_DIR
                        Path containing schemata json files
  -g KAFKA_REQ_GEN, --kafka-req-gen KAFKA_REQ_GEN
                        Path to the kafka request generator
  --request-output-dir REQUEST_OUTPUT_DIR
                        Output directory for generated requests
  --response-output-dir RESPONSE_OUTPUT_DIR
                        Output directory for generated responses
```

* `schema-data`
  * Path to the directory containing the schema JSON files
  * Example `redpanda/src/v/kafka/protocol/schemata`
* `kafka-req-gen`
  * Path to the compiled `kafka-request-generator` GO aplication
  * Example: `vbuild/debug/clang/src/go/kreq-gen/kafka-request-generator`
* `request-output-dir`
  * Path to the corpus directory that is utilized by the Kafka request parsing fuzzer
  * This is where the generated request messages will be placed
* `response-output-dir`
  * Path to the corpus directory that is utilized by the Kafka response parsing fuzzer
  * This is there the generated response messages will be placed
