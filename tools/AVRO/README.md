# How to install Kafka
## Using docker
```bash
# set the Kafka version you want to use
KAFKA_VERSION=3.7.1
docker run -p 9092:9092 apache/kafka:${KAFKA_VERSION}
```
## Installation
```bash
# set the Kafka version you want to use
KAFKA_VERSION=3.7.1
KAFKA_RELEASE=2.13
sudo apt update
sudo apt install openjdk-11-jdk -y
mkdir /tmp/kafka
cd /tmp/kafka
wget https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${KAFKA_RELEASE}-${KAFKA_VERSION}.tgz
tar xvf kafka_${KAFKA_RELEASE}-${KAFKA_VERSION}.tgz
sudo mv kafka_${KAFKA_RELEASE}-${KAFKA_VERSION} /usr/local/kafka
cat <<- "EOF" > zookeeper.service
[Unit]
Description=Apache Zookeeper server
Documentation=http://zookeeper.apache.org
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
ExecStart=/usr/local/kafka/bin/zookeeper-server-start.sh /usr/local/kafka/config/zookeeper.properties
ExecStop=/usr/local/kafka/bin/zookeeper-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF
sudo mv zookeeper.service /etc/systemd/system/zookeeper.service
cat <<- "EOF" > kafka.service
[Unit]
Description=Apache Kafka Server
Documentation=http://kafka.apache.org/documentation.html
Requires=zookeeper.service

[Service]
Type=simple
Environment="JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"
ExecStart=/usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/server.properties
ExecStop=/usr/local/kafka/bin/kafka-server-stop.sh

[Install]
WantedBy=multi-user.target
EOF
sudo mv kafka.service /etc/systemd/system/kafka.service
````
## Start the daemons
```bash
sudo systemctl daemon-reload
sudo systemctl start zookeeper
sudo systemctl start kafka
```
## Create a topic
```bash
cd /usr/local/kafka
bin/kafka-topics.sh \
  --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic sample.to.pic
```
## List topics
```bash
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```
## Send and Receive a Message in Kafka
Producer:
```bash
bin/kafka-console-producer.sh --broker-list localhost:9092 --topic sampleTopic
```
When prompted add a message.
Consumer:
```bash
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic sampleTopic --from-beginning
```