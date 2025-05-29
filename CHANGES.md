# SCIMMA Server Container Changes
## May 29, 2025
Version 0.9.0

    1. Update to hop-client version 0.11.1

## May 25, 2023
Version 0.8.1

    1. Update version of confluent-kafka-python

## May 25, 2023
Version 0.8.0

    1. Update to scimma/base:0.5.1
    2. Update to hop-client 0.8.0

## May 16, 2022
Version 0.7.1

   1. Update Hop client to version 0.5.1

## Apr 22, 2022
Version 0.7.0

   1. Update Hop client to version 0.5.0

## Feb 4, 2022
Version 0.6.0

   1. Update scimma/base to scimma/base:0.4.0
      This changes the base operating system to Rocky Linux 8.5.

## Sep 30 2021
Version 0.5.3

   1. Update scimma/base to scimma/base:0.3.2 to address
      https://github.com/scimma/scimma-server-container/issues/63

## Sep 23, 2021
Version 0.5.2

   1. Update scimma/base to scimma/base:0.3.2

## Sep 22, 2021
Version 0.5.0

   1. Update scimma/base to scimma/base:0.3.0

## Jul 6, 2021
Version 0.4.0

   1. Update hop client to 0.4.0


## Mar 20, 2021
Version 0.3.1

   1. Update scimma/base dependency to scimma/base:0.2.0
   2. Update hop client to version 0.2.0

## Aug 5, 2020

Version 0.2.0

  1. Updated hop client to version 0.1

  2. Added ``--advertisedListener`` option to the server container.

  3. In (doc/HopskotchDev.md), suggest using SCRAM credentials. The older
     PLAIN credentials are on the road to deprecation. In a future release,
     the server container will use SCRAM credentials like ``dev.hop``.

## May 8, 2020

Version 0.1.9

   1. Added "connect to HOP development infrastructure" use case.
   
   2. Updated hop client version to 0.0.5.

## Mar 4, 2020

Version 0.1.8

   1. Replaced test framework with Python equivalent.

   2. Added the scimma client to the client container.

   3. Removed the docker-compose based use case.

   4. Now explicitly configure Kafka to advertise a listener
      with the IP address of the host instead of the hostname
      of the host. The hostname of the host might not be
      resolvable everywhere that might connect to the container.

## Feb 21, 2020

Version 0.1.7

  1. Replaced runServer/configureSSL.pl with a Python equivalent.

  2. Added --noSecurity option to start the Kafka server without
     SSL and user authentication

  3. Added --javaDebugSSL option to start the Kafka server with
     JAVA SSL debugging turned on.

  4. Modified Dockerfiles so that they depend on a specific
     scimma/base version. For now, that version is 0.1.1


## Feb 16, 2020

Version 0.1.6

  1. Switched to scimma/base:0.0 which updates OpenJDK from 8 to 11. 

  2. Modified configureSSL.pl to generate an RSA key instead of a DSA key.
     This fixes an issue where kafkacat under macOS could not negotiate a cipher suite with the server.

## Feb 5, 2020

Version:  0.1.5

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

## Jan 23, 2020

TAG: 20200123-001

Initial development. The scimma-server container merely runs kafka. The client
has an installation of kafka without zookeper. You can run 

    * kafka-console-producer.sh
    * kafka-console-consumer.sh

in the scimma-client container to verify that the client and server can communicate and that kafka is
functioning.

