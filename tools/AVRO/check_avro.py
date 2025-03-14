#!/bin/env python3

# Repository:   https://github.com/Python-utilities
# File Name:    tools/AVRO/check_avro.py
# Description:  Send AVRO messages on Kafka
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

import argparse
import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.logger import error, log_warning
from tools.AVRO.avro_kafka import AvroKafka


def argument_error(error_message: str, parser: argparse.ArgumentParser):
    log_warning(f"Argument error:\n{parser.format_help()}")
    error(error_message)


def parse_and_validate_arguments():
    parser = argparse.ArgumentParser(description='Checking, producing and consuming of AVRO messages')
    command_group = parser.add_argument_group(title="commands", description="command to execute")
    command_group.add_argument("--resend", "-r",
                               default=False,
                               action='store_true',
                               help='resend message at partition (--partition) and offset (--offset)')
    command_group.add_argument("--check-avro", "-c",
                               default=False,
                               action='store_true',
                               help='Check whether the data-file (--data-file) conforms to schema (--schema-file)')
    command_group.add_argument("--prod-con", "-P",
                               default=False,
                               action='store_true',
                               help='Run a producer->consumer chain for the given message '
                                    '(needs: --data-file, --schema-file, --topic)')
    parser.add_argument("--schema-file", "-s",
                        default="schema.avsc",
                        type=str,
                        help='Schema file to check against, default "schema.avsc"')
    parser.add_argument("--data-file", "-d",
                        default="data.json",
                        type=str,
                        help='Json file containing the message, default "data.json"')
    parser.add_argument("--topic", "-t",
                        type=str,
                        default="some.topic.of.mine",
                        nargs='+',
                        help='topics to subscribe/post to, default "some.topic.of.mine"')
    parser.add_argument("--partition", "-p",
                        type=int,
                        default=None,
                        help='Partition where to find a resend message, default: 0')
    parser.add_argument("--offset", "-o",
                        type=int,
                        default=None,
                        help='offset of the message to resend, default: 0')
    parser.add_argument("--kafka-server", "-k",
                        default='localhost:9092',
                        type=str,
                        help='Kafka server to connect to, default "localhost:9092"')
    args = parser.parse_args()

    if not args.resend and not args.check_avro and not args.prod_con:
        argument_error("No command given: choose from --resend, --check-avro or --prod-con", parser)

    if not args.schema_file:
        argument_error("No schema given: requires a --schema", parser)
    if not args.data_file:
        argument_error("No data-file given: requires a --data-file", parser)
    if args.resend:
        if not args.topic:
            argument_error("No topic given: resending a message requires a --topic", parser)
        if args.partition is None:
            argument_error("No partition given: resending a message requires a --partition", parser)
        if args.offset is None:
            argument_error("No offset given: resending a message requires an --offset", parser)
    if args.prod_con:
        if not args.topic:
            argument_error("No topic given: producing/consuming a message requires a --topic", parser)

    return args


if __name__ == '__main__':
    found_args = parse_and_validate_arguments()

    producer_conf = {'bootstrap.servers': found_args.kafka_server}
    consumer_conf = {
        'bootstrap.servers': found_args.kafka_server,
        'group.id': 'my_group',
        'auto.offset.reset': 'earliest'
    }
    avro_kafka = AvroKafka(schema_path=found_args.schema_file,
                           json_path=found_args.data_file,
                           consumer_conf=consumer_conf,
                           producer_conf=producer_conf)
    avro_kafka.load_json(found_args.data_file)
    if found_args.resend:
        avro_kafka.query_and_resend_message(topic=found_args.topic,
                                            partition=found_args.partition,
                                            offset=found_args.offset)
    if found_args.check_avro:
        avro_kafka.validate_json_against_schema()
    if found_args.prod_con:
        avro_kafka.query_and_resend_message(topic=found_args.topic,
                                            partition=found_args.partition,
                                            offset=found_args.offset)
