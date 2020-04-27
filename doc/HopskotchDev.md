# Connect to the HOPSKOTCH Development Server

This page describes one way to use the client container to connect to the HOPSKOTCH development server (``dev.hop.scimma.org``; referred to as ``dev.hop`` below).

### Configuration

To connect to ``dev.hop``, ``kafkacat`` will need the following configuration items:

```
security.protocol=SASL_SSL
sasl.username=USERNAME
sasl.password=PASSWORD
sasl.mechanism=PLAIN
ssl.ca.location=/etc/pki/tls/certs/ca-bundle.trust.crt

```

These can be given on the command line using ``-X`` or put in a file. In this example, they are put in the current working directory
and the current working directory is mapped to ``/root/shared`` in the container. The ``kafkacat`` program in the client container
expects to find the configuration file there.

Assuming that the file ``kafakacat.conf`` exists in the current working directory of your shell with the above content (with ``USERNAME`` and ``PASSWORD`` substituted with your actual credentials), the following
commands should work:

```
docker run -i --rm=true -v `pwd`:/root/shared scimma/client:latest kafkacat -L -b dev.hop.scimma.org:9092
docker run -i --rm=true -v `pwd`:/root/shared scimma/client:latest kafkacat -P -b dev.hop.scimma.org:9092 -t test
docker run -i --rm=true -v `pwd`:/root/shared scimma/client:latest kafkacat -C -b dev.hop.scimma.org:9092 -t test -e
docker run -i --rm=true -v `pwd`:/root/shared scimma/client:latest kafkacat -C -b dev.hop.scimma.org:9092 -t gcn  -e

```
