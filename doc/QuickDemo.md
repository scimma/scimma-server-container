# SCiMMA Server Container Demo

This is a very script-like demo that does not involve any non-docker commands on the local machine and that does
not hide what is going on like ``docker-compose``.
You should be able to copy and paste these commands anywhere that you run docker.

## The Commands:

```
docker network create scimma-net
docker run -d --rm=true --network=scimma-net --name=scimma-server -v shared:/root/shared scimma/server:latest

docker run -i --rm=true --network=scimma-net -v shared:/root/shared scimma/client:latest kafkacat -P -b scimma-server:9092 -t test
docker run -i --rm=true --network=scimma-net -v shared:/root/shared scimma/client:latest kafkacat -L -b scimma-server:9092
docker run -i --rm=true --network=scimma-net -v shared:/root/shared scimma/client:latest kafkacat -C -b scimma-server:9092 -t test -e

docker run -i --rm=true --network=scimma-net -v shared:/root/shared scimma/client:latest scimma publish  -F /root/shared/kafkacat.conf  -b kafka://scimma-server:9092/gcn /root/test_data/example.gcn3
docker run -i --rm=true --network=scimma-net -v shared:/root/shared scimma/client:latest kafkacat -C -b scimma-server:9092 -t gcn -e

docker kill scimma-server
docker network rm scimma-net

```

The first kafkacat command (with the ``-P`` option) may appear to hang, but it is waiting for input. Each input line is a message. End with ``Ctrl-D`` or ``Ctrl-C``.

The rest of this page just explains the above commands.

### Create a Network

```
        docker network create scimma-net
```

Create a docker network named ``scimma-net``.
The main benefit to creating a network is that container names automatically become resolvable using DNS.

### Create the Server

```
     docker run -d --rm=true --network=scimma-net --name=scimma-server -v shared:/root/shared scimma/server:latest
```

Start a container using the image ``scimma/server:latest``.

Options:

| Option |  Description |
|--------|:-------------|
| *-d*   |  run in the background (detach) |
| *--rm=true* | delete the container after it exits |
| *--network=scimma-net*  | create an interface on the netowrk ``scimma-net`` |
| *--name=scimma-server*   | use ``scimma-server`` as the name of the container | 
| *-v shared:/root/shared* | create a named volumen named ``shared``   |


### Client Options

These options are common to the following ``scimma/client`` container commands.

| Option |  Description |
|--------|:-------------|
| *-i*   |  run container interactively (in the foreground) |
| *--rm=true* | delete the container after it exits |
| *--network=scimma-net* | create an interface on the netowrk ``scimma-net`` |
| *-v shared:/root/shared* | mount the named volume ``shared`` as ``/root/shared`` inside the container |

### Publish Messages

```
docker run -i --network=scimma-net -v shared:/root/shared scimma/client:latest kafkacat -P -b scimma-server:9092 -t test
```

Start a container based on the image ``scimma-client:latest`` and inside the container, run
the command:


```
    kafkacat -P -b scimma-server:9092 -t test
 ```

Notice that the broker is specified using the name ``scimma-server`` which can be resolved inside the container
because we are using the netowrk ``scimma-net``.

This command reads from standard input and publishes one message for each line that it reads. You could pipe
a file like so:

    ```
        cat MYFILE.txt | docker run -i --network=scimma-net -v shared:/root/shared scimma/client:latest kafkacat -P -b scimma-server:9092 -t test
    ```

### List Metadata

```
docker run -i --network=scimma-net -v shared:/root/shared scimma/client:latest kafkacat -L -b scimma-server:9092
```

Start a container based on the image ``scimma-client:latest`` and inside the container, run
the command:

```
    kafkacat -L -b scimma-server:9092
```

### Consume Messages

```
docker run -i --network=scimma-net -v shared:/root/shared scimma/client:latest kafkacat -C -b scimma-server:9092 -t test -e
```

Start a container based on the image ``scimma-client:latest`` and inside the container, run
the command:

```
    kafkacat -C -b scimma-server:9092 -t test -e
```

### Publish a GCN
```
docker run -i --network=scimma-net -v shared:/root/shared scimma/client:latest scimma publish  -F /root/shared/kafkacat.conf  -b kafka://scimma-server:9092/gcn /root/test_data/example.gcn3
```

This command runs the scimma command in a container. The file ``example.gcn3`` is included as part of the container. You could mount a local directory
containing GCNs as a volume in the client container and have the scimma client read files there.

Note that the Kafka topic, ``gcn``, is specified as part of the URL.

### Read the GCN
```
docker run -i --network=scimma-net -v shared:/root/shared scimma/client:latest kafkacat -C -b scimma-server:9092 -t gcn -e
```

This uses ``kafkacat`` in the client container to read the ``gcn`` topic.

### Clean Up

```
docker kill scimma-server
docker network rm scimma-net
```

Shut down and remove the container ``scimma-server`` and remove the network ``scimma-net``.
