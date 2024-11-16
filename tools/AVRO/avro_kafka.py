# Repository:   https://github.com/Python-utilities
# File Name:    tools/AVRO/avro_kafka.py
# Description:  Class handling the checking and sending AVRO messages on Kafka
#
# Copyright (C) 2023 Dieter J Kybelksties <github@kybelksties.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# @date: 2024-07-13
# @author: Dieter J Kybelksties

from os import PathLike
import fastavro
from fastavro.schema import load_schema
from fastavro import writer, reader
from confluent_kafka import Producer, Consumer, KafkaError, TopicPartition
from io import BytesIO

from lib.json_object import JsonObject


class AvroKafka:
    def __init__(self,
                 json_path: PathLike | str,
                 schema_path: PathLike | str,
                 consumer_conf,
                 producer_conf
                 ):
        self.json_ = None
        self.load_json(json_path)
        self.schema_ = None
        self.load_avro_schema(schema_path)
        self.producer = Producer(producer_conf)
        self.consumer = Consumer(consumer_conf)

    def load_json(self, file_path: PathLike | str):
        """
        Load a JSON document from file.
        :param file_path: JSON document to check against schema
        """
        self.json_ = JsonObject(filename=file_path)

    def load_avro_schema(self, file_path: PathLike | str):
        """
        Load as AVRO schema document from file.
        :param file_path: A document to check against schema
        """
        self.schema_ = load_schema(str(file_path))

    def validate_json_against_schema(self):
        """
        Validate JSON against schema against avro schema.
        :return: true if valid, false otherwise
        """
        return fastavro.validation.validate(self.json_.get_json(), self.schema_)

    def serialize_to_avro(self):
        """
        Serialize JSON document using the AVRO schema.
        :return: serialized Jason as bytes
        """
        bytes_writer = BytesIO()
        writer(bytes_writer, self.schema_, [self.json_.get_json()])
        return bytes_writer.getvalue()

    def deserialize_from_avro(self, avro_data):
        """
        Deserialize JSON document using the AVRO schema.
        :param avro_data:
        :return:
        """
        bytes_reader = BytesIO(avro_data)
        reader_generator = reader(bytes_reader, self.schema_)
        for record in reader_generator:
            return record

    def produce_to_kafka(self, topic):
        """
        Produce a Kafka message to Kafka.
        :param topic: topic of the message
        """
        avro_data = self.serialize_to_avro()
        self.producer.produce(topic, avro_data)
        self.producer.flush()
        print(f"Produced data to topic '{topic}'")

    def consume_from_kafka(self, topics: str | list[str]):
        """
        Consume a Kafka message on Kafka.
        :param topics: the topics to consume
        :return:
        """
        if isinstance(topics, str):
            topics = [topics]
        self.consumer.subscribe(topics)
        while True:
            msg = self.consumer.poll(timeout=1.0)
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
                deserialized_data = self.deserialize_from_avro(avro_data)
                print("Consumed and deserialized data:", deserialized_data)
            except Exception as e:
                print(f"Failed to deserialize Avro data: {e}")
            break

    def query_and_resend_message(self,
                                 topic: str,
                                 partition: int,
                                 offset: int):
        """
        Query a Kafka message at a specific partition and offset and resend it.
        :param topic: Topic to query and resend the message from.
        :param partition: Partition to query.
        :param offset: Offset to query.
        """
        self.consumer.assign([TopicPartition(topic, partition, offset)])
        msg = self.consumer.poll(timeout=10.0)
        if msg is None:
            print(f"No message found at partition {partition} and offset {offset}.")
            return
        if msg.error():
            print(f"Error querying message: {msg.error()}")
            return

        avro_data = msg.value()
        deserialized_data = self.deserialize_from_avro(avro_data)
        print(f"Queried and deserialized data: {deserialized_data}")

        self.produce_to_kafka(topic)
        # consumer.close()
