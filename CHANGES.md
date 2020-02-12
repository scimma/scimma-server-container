# SCIMMA Server Container Changes

## Jan 23, 2020

TAG: 20200123-001

Initial development. The scimma-server container merely runs kafka. The client
has an installation of kafka without zookeper. You can run 

    * kafka-console-producer.sh
    * kafka-console-consumer.sh

in the scimma-client container to verify that the client and server can communicate and that kafka is
functioning.

## Feb 5, 2020

Version:  0.1

Container changes:

  1. The containers now use Confluent RPMs instead of tar files.
  2. Due to 1, the demo changed slightly. There is no longer a 
     ".sh" extension on the commands in the client container.
  3. The working directory for the client container is now /usr/bin
     instead of /opt/kafka/bin.
  4. The client container now has a build of kafkacat
  5. The client container used to have an ENTRYPOINT, now
     it only has a CMD. This has the effect of allowing the user 
     to override "/bin/bash" on the command line. You can now run, for example:

        docker network create scimma-test
        docker run -p 9092:9092 --detach=true --rm=true --network=scimma-test --name=scimma-test-srv scimma/server:latest
        cat foo.txt | docker run  -i --network=scimma-test -link=scimma-test-srv scimma/client:latest /usr/local/bin/kafkacat -P -b scimma-test-srv:9092 -t test
        docker run  -i --network=scimma-test -link=scimma-test-srv scimma/client:latest /usr/local/bin/kafkacat -C -b scimma-test-srv:9092 -t test  -o -5 -e

     to send the lines of the file foo.txt as messages and retrieve the last 5 messages.

  6. There is "test" make target. It is basic at the moment, but it does have non-trivial tests.

  7. Communications between the Kafka broker and clients are encrypted by default and a password is required.

     To support this there are now command line options on the server container:

         --brokerUser=BUSER
              The user for inter-broker communication. Default: admin

         --brokerPass=BPASS
              The password for inter-broker communication. Default: admin-secret

         --users=USER:PASS,...
               Additional users and passwords. Default: test:test-pass

         --keyPass=KPASS
               The password used for Java keystores and truststores. Default: 123456

     Kafkacat requires that the server certificate be signed by a trusted certificate
     authority. The certificate authority certificate can be downloaded from the
     server container using "docker cp":

         docker cp SERVER_CONTAINER_ID:/root/shared/tls/cacert.pem cacert.pem

     An example kafkacat command line using SSL/TLS and PLAIN authentication:

         kafkacat -P -b scimma-server:9092 -t test -X sasl.mechanism=PLAIN -X sasl.username=test -X sasl.password=test-secret -X security.protocol=SASL_SSL -X ssl.ca.location=cacert.pem

     A kafkacat config file is created by the server that contains the necessary
     properties so that the "-X" options are not necessary. It can be downloaded
     like so:

```
        mkdir ~/.config
        docker cp SERVER_CONTAINER_ID:/root/shared/kafkacat.conf ~/.config/kafkacat.conf
```

  8. The common and stable parts of Dockerfile.client and Dockerfile.server have been
     factored into a new container: scimma/base.

  9. Modification for workflow demo.
