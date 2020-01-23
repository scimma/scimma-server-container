# SCIMMA Server Container Changes

## Jan 23, 2020

Initial development. The scimma-server container merely runs kafka. The client
has an installation of kafka without zookeper. You can run 

    * kafka-console-producer.sh
    * kafka-console-consumer.sh

in the scimma-client container to verify that the client and server can communicate and that kafka is
functioning.

