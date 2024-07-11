#!/bin/env python3

import json
from os import PathLike
import fastavro
from fastavro.schema import load_schema
from fastavro import writer, reader
from confluent_kafka import Producer, Consumer, KafkaError
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


def consume_from_kafka(consumer, avro_schema: str | list | dict):
    """
    Consume a Kafka message on Kafka.
    :param consumer: the consumer
    :param avro_schema: the AVRO schema to use for the deserialization
    :return:
    """
    consumer.subscribe(['avro_topic'])
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


def json_to_xml(json_obj, line_padding=""):
    """Converts JSON object to XML string.

    Args:
        json_obj (dict): The JSON object to convert.
        line_padding (str): Line padding for formatting (used for nested elements).

    Returns:
        str: The XML string representation of the JSON object.
    """

    def dict_to_xml(tag, d):
        elem = Element(tag)
        if isinstance(d, dict):
            for key, val in d.items():
                child = SubElement(elem, key)
                if isinstance(val, dict):
                    child.extend(dict_to_xml(key, val))
                elif isinstance(val, list):
                    for sub_dict in val:
                        child.extend(dict_to_xml(key, sub_dict))
                else:
                    child.text = str(val)
        else:
            elem.text = str(d)
        return elem

    root_tag = list(json_obj.keys())[0]
    root_elem = dict_to_xml(root_tag, json_obj[root_tag])
    return tostring(root_elem).decode()


def main(json_file_path: PathLike | str,
         topic: str | list | dict,
         avro_schema_file_path: PathLike | str,
         kafka_bootstrap_servers: str):
    # Load the JSON document
    json_data = load_json(json_file_path)

    print(json_to_xml(json_data))

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
    consume_from_kafka(consumer, avro_schema)
    consumer.close()


if __name__ == '__main__':
    json_file_path = 'data.json'
    topic = 'some.to.pic'
    avro_schema_file_path = 'schema.avsc'
    kafka_bootstrap_servers = 'localhost:9092'
    main(json_file_path, topic, avro_schema_file_path, kafka_bootstrap_servers)
