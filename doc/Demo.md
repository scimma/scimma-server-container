## SCIMMA Server Container Demo

Run the scimma-server service:

``` sh
   docker-compose up -d scimma-server
```

This starts the scimma server container in the background. You can verify that it is running
with:

        docker ps
   
Run the scimma-client service:

``` sh
    docker-compose run scimma-client
```

This starts the scimma client container in the foreground. You will immediately get a shell in the scimma
client container.

Because the containers were strarted using docker-compose, some 
network names exist. In the client you can do:

``` sh
        nslookup scimma-server
```

and you should see output like:

``` sh
root@ef7b388c7359 bin]# nslookup scimma-server
Server:         127.0.0.11
Address:        127.0.0.11#53

Non-authoritative answer:
Name:   scimma-server
Address: 172.19.0.2

```

## Send some test messages:

Run:

``` sh
        ./kafka-console-producer.sh --broker-list scimma-server:9092 --topic=test
```

and enter several messages one per line. The content is not important. You may see
some java warnings. As long as the kafka-console-producer.sh continues to read
standard input, you can ignore the messages.

When you are done entering messages, type Ctrl-d.

## Receive the messages.

Run the command (in the scimma-client container):

``` sh
    ./kafka-console-consumer.sh --bootstrap-server scimma-server:9092 --topic=test --from-beginning
```
You should see the messages that you sent.

## Extra credit

You can run a second shell on the scimma/client container.

Leave the window with ./kafka-console-consumer.sh running.
In another window (as root), run:

``` sh
    docker ps
```

to find the container id of the scimma/client container. Then, as root, run:

``` sh
   docker exec -it CONTAINER_ID /bin/bash
```

where CONTAINER_ID is the container id of the scimma/client container. You can now run the ./kafka-console-producer.sh 
as above in one of the windows and ./kafka-console-consumer.sh as above in the other.

When you type a message in the window running kafka-console-producer.sh, you should see the message appear
in the window running kafka-console-consumer.sh right after you hit return.
