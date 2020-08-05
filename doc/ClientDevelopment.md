## Client Development 

For SCIMMA client development on the user's host, it is convenient to use the SCIMMA server container like so:

```sh
    docker run --rm -p 9092:9092 --hostname localhost scimma/server

```

This will download and run an instance of scimma/server that listens to port 9092 on the localhost.

The user can then point client software at:

```sh
       localhost:9092
```

for development and testing.

## Kafka Data

The Kafka server in the scimma/server container stores data in the container in the directory ``/tmp/kafka-logs``. It normally doesn't persist between
server runs. To persist data between server runs, an option like:

```
   -v /local/path/kafka-logs:/tmp/kafka-logs
```

can be given to ``docker run`` to associate ``/tmp/kafka-logs`` in the container with ``/local/path/kafka-logs`` on the host.

## SSL/Auth data

The scimma/server container stores a kafkacat configuration file (``kafkacat.conf``) and the CA certificate for the CA that signs the Kafka server's certificate (``cacert.pem``) under ``/root/shared`` in the container. To have easy access to these files it can be convenient to user an option like:

```
    -v /local/path/shared:/root/shared
```

## Putting it all together

An example command line that persists data to a host directory (``/tmp/kafka-logs``) and stores SSL info and the kafkacat config file under a host directry (``/tmp/shared``) is:

```
    docker run -p 9092:9092 -v /tmp/kafka-logs:/tmp/kafka-logs -v /tmp/shared:/root/shared  --hostname localhost scimma/server
```


## Notes:

The hostname of the server is sent to kafka clients and the clients use the hostname to resolve to an IP address *even if* they are already connected to the kafka server (for example, by directly using the localhost IP address). It is, therefore, necessary to set the hostname of the server to a string that the client can resolve.

In the case above, the server is listening on the host machine's localhost address so ``localhost`` is used as the hostname.
