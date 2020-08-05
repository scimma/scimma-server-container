# Connect to the HOPSKOTCH Development Server

This page describes one way to use the client container to connect to the HOPSKOTCH development server (``dev.hop.scimma.org``; referred to as ``dev.hop`` below).

### Configuration

To connect to dev.hop, kafkacat will need the following configuration items:

```
security.protocol=SASL_SSL
sasl.username=USERNAME
sasl.password=PASSWORD
sasl.mechanism=SCRAM-SHA-512
ssl.ca.location=/etc/pki/tls/certs/ca-bundle.trust.crt
```

Note that this configuration uses a different ``sasl.mechanism`` than that used for authentication to the ``scimma/server-container`` container.

The username/password pair can be generated on [the Hop Admin website](https://admin.dev.hop.scimma.org/hopauth).

The configuration items can be specified on the command line using ``-X`` or put in a file. In this example, they are put in a file in the current working directory
and the current working directory is mapped to ``/root/shared`` in the container. The ``kafkacat`` program in the client container
expects to find the configuration file there.

Assuming that the file ``kafakacat.conf`` exists in the current working directory of your shell with the above content (with ``USERNAME`` and ``PASSWORD`` substituted with your actual credentials), the following
commands should work:

```
docker run -i --rm=true -v `pwd`:/root/shared scimma/client:latest kafkacat --help
docker run -i --rm=true -v `pwd`:/root/shared scimma/client:latest kafkacat -L -b dev.hop.scimma.org:9092
docker run -i --rm=true -v `pwd`:/root/shared scimma/client:latest kafkacat -C -b dev.hop.scimma.org:9092 -t gcn -o -1 -e
docker run -i --rm=true -v `pwd`:/root/shared scimma/client:latest kafkacat -C -b dev.hop.scimma.org:9092 -u -t heartbeat  2>/dev/null
```

These commands:

1. Print the help text for the ``kafkacat`` command.
2. List the available topics, partitions and brokers.
3. Consume the last message in the `gcn` topic.
4. Consume messages sent to the heartbeat topic. There should be one every 30 seconds. You may have to wait up to 30 seconds to get the first message. You will have to use ``Ctrl-C`` to stop the process.


### The Hop Client

The above details how you can use the kafkacat Kafka client to access ``dev.hop``. You can also use the hop command line client which can be run using docker like so:

```
docker run -i --rm=true -v `pwd`:/root/shared scimma/client:latest hop COMMAND ARGS
```

where your configuration file is located in your current working directory. For information about the hop client see [the hop client documentation](https://hop-client.readthedocs.io/en/stable/).

You can also run the client container like so:

```
docker run -it --rm=true -v `pwd`:/root/shared scimma/client:latest /bin/bash
```

to run a bash shell in the container. Within that shell, you can run hop client commands.
