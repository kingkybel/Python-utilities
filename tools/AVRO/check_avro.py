#!/bin/env python3

import argparse
import json
from os import PathLike
import fastavro
from fastavro.schema import load_schema
from fastavro import writer, reader
from confluent_kafka import Producer, Consumer, KafkaError, TopicPartition
from io import BytesIO
from xml.etree.ElementTree import Element, tostring, SubElement


def load_json(file_path: PathLike | str):
    """
    Load a JSON document from file.
    :param file_path: JSON document to check against schema
    :return: read JSON document
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def load_avro_schema(file_path: PathLike | str):
    """
    Load as AVRO schema document from file.
    :param file_path: A document to check against schema
    :return: the AVRO schema
    """
    return load_schema(str(file_path))


def validate_json_against_schema(json_data, avro_schema: str | list | dict):
    """
    Validate JSON against schema against avro schema.
    :param json_data: JSON document to check
    :param avro_schema: AVRO schema to validate against
    :return: true if valid, false otherwise
    """
    return fastavro.validation.validate(json_data, avro_schema)


def serialize_to_avro(json_data, avro_schema: str | list | dict):
    """
    Serialize JSON document using the AVRO schema.
    :param json_data: the JSON document to serialize
    :param avro_schema: the AVRO schema to use for the serialization
    :return: serialized Jason as bytes
    """
    bytes_writer = BytesIO()
    writer(bytes_writer, avro_schema, [json_data])
    return bytes_writer.getvalue()


def deserialize_from_avro(avro_data, avro_schema: str | list | dict):
    """
    Deserialize JSON document using the AVRO schema.
    :param avro_data:
    :param avro_schema:
    :return:
    """
    bytes_reader = BytesIO(avro_data)
    reader_generator = reader(bytes_reader, avro_schema)
    for record in reader_generator:
        return record


def produce_to_kafka(producer, topic, avro_data):
    """
    Produce a Kafka message to Kafka.
    :param producer: the producer
    :param topic: topic of the message
    :param avro_data: AVRO data - payload
    """
    producer.produce(topic, avro_data)
    producer.flush()
    print(f"Produced data to topic '{topic}'")


def consume_from_kafka(consumer, avro_schema: str | list | dict, topic: str):
    """
    Consume a Kafka message on Kafka.
    :param consumer: the consumer
    :param avro_schema: the AVRO schema to use for the deserialization
    :return:
    """
    consumer.subscribe([topic])
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
        avro_data = msg.value()
        try:
            deserialized_data = deserialize_from_avro(avro_data, avro_schema)
            print("Consumed and deserialized data:", deserialized_data)
        except Exception as e:
            print(f"Failed to deserialize Avro data: {e}")
        break


def query_and_resend_message(consumer_conf,
                             producer_conf,
                             topic: str,
                             partition: int,
                             offset: int,
                             avro_schema: str | list | dict):
    """
    Query a Kafka message at a specific partition and offset and resend it.
    :param consumer_conf: Configuration for the Kafka consumer.
    :param producer_conf: Configuration for the Kafka producer.
    :param topic: Topic to query and resend the message from.
    :param partition: Partition to query.
    :param offset: Offset to query.
    :param avro_schema: Avro schema for deserialization.
    """
    consumer = Consumer(consumer_conf)
    consumer.assign([TopicPartition(topic, partition, offset)])
    msg = consumer.poll(timeout=10.0)
    if msg is None:
        print(f"No message found at partition {partition} and offset {offset}.")
        return
    if msg.error():
        print(f"Error querying message: {msg.error()}")
        return

    avro_data = msg.value()
    deserialized_data = deserialize_from_avro(avro_data, avro_schema)
    print(f"Queried and deserialized data: {deserialized_data}")

    producer = Producer(producer_conf)
    produce_to_kafka(producer, topic, avro_data)
    consumer.close()


def main(json_file_path: PathLike | str,
         topic: str,
         avro_schema_file_path: PathLike | str,
         kafka_bootstrap_servers: str,
         partition: int = None,
         offset: int = None):
    # Load the JSON document
    json_data = load_json(json_file_path)

    # Load the Avro schema
    avro_schema = load_avro_schema(avro_schema_file_path)

    # Validate the JSON document against the Avro schema
    is_valid = validate_json_against_schema(json_data, avro_schema)

    if is_valid:
        print("The JSON document is valid against the Avro schema.")
    else:
        print("The JSON document is NOT valid against the Avro schema.")
        return

    # Serialize the JSON document to Avro binary format
    avro_data = serialize_to_avro(json_data, avro_schema)

    # Produce the serialized Avro data to Kafka
    producer_conf = {'bootstrap.servers': kafka_bootstrap_servers}
    producer = Producer(producer_conf)
    produce_to_kafka(producer, topic, avro_data)

    # Consume the Avro data from Kafka and deserialize it
    consumer_conf = {
        'bootstrap.servers': kafka_bootstrap_servers,
        'group.id': 'my_group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_conf)
    consume_from_kafka(consumer, avro_schema, topic)
    consumer.close()

    # If partition and offset are provided, query and resend the message
    if partition is not None and offset is not None:
        query_and_resend_message(consumer_conf, producer_conf, topic, partition, offset, avro_schema)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Checking, producing and consuming of AVRO messages')
    parser.add_argument("--schema-file", "-s",
                        default="schema.avsc",
                        type=str,
                        help=f'Root directory for the project, default "schema.avsc"')
    parser.add_argument("--data-file", "-d",
                        default="data.json",
                        type=str,
                        help='Json file containing the message to check against the schema/produce on Kafka,"'
                             '" default "data.json"')
    parser.add_argument("--topic", "-t",
                        type=str,
                        default="some.topic.of.mine",
                        nargs='+',
                        help='topics to subscribe/post to, default "some.topic.of.mine"')
    parser.add_argument("--partition", "-p",
                        type=int,
                        default=0,
                        help='Partition where to find a resend message, default: 0')
    parser.add_argument("--offset", "-o",
                        type=int,
                        default=0,
                        help='offset of the message to resend, default: 0')
    parser.add_argument("--resend", "-r",
                        default=False,
                        action='store_true',
                        help='resend message at partition (--partition) and offset (--offset)')
    parser.add_argument("--kafka-server", "-k",
                        default='localhost:9092',
                        type=str,
                        help='Kafka server to connect to, default "localhost:9092"')

    found_args = parser.parse_args()

    avro_schema_file_path = found_args.schema_file
    json_file_path = found_args.data_file
    topic = found_args.topic
    kafka_bootstrap_servers = found_args.kafka_server
    partition = found_args.partition
    offset = found_args.offset
    main(json_file_path, topic, avro_schema_file_path, kafka_bootstrap_servers, partition, offset)
