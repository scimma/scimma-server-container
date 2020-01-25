## SCIMMA Server Container

The SCIMMA Server Container provides a development version of the SCIMMA server infrastructure which includes:

    1. A Kafka server.
    2. A Zookeeper installation used by the Kafka server
    3. SCIMMA server processes that consume and produce Kafka messages.

The SCIMMA Server Container is intended to be useful for:

    1. SCIMMA integration testing
    2. SCIMMA development 
    3. SCIMMA client (both producer and consumer) development

The SCIMMA Server Container is most definitely **NOT** an example of 
best practice kafka infrastructure implementation. These
containers are for testing, not for production.

## Prerequisites:

        0. VirtualBox (Mac Only)
        1. Build tools: GNU Make, curl, git
        2. Working docker installation
        3. Working docker-compose installation

## Download

Clone the SCIMMA server git repository:

```
   git clone git@github.com:scimma/scimma-server-container.git
```

## Build

Build the containers using GNU make:

```
   cd scimma-server-container
   make
```

The ``make``step is not strictly necessary. If you don't run make, and you continue
to the next stop, docker-compose will get the containers from dockerhub.com.

## Verify the Installation

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

## Send some test message:

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


## Mac Specific Notes

The containers have been tested using:

    1. The built-in make, curl, and git in macOS Catalina 10.15.1.
    2. Docker from mac ports (https://www.macports.org/)
    3. Docker compose downloaded via:

``` sh
           curl -L https://github.com/docker/compose/releases/download/1.25.3/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
           chmod +x /usr/local/bin/docker-compose
```

The docker-compose provided by mac ports did not work when tested.

In order to run Docker commands, that is, to have a working docker installation
when using docker from Mac Ports and VirtualBox, you will need to manually setup
your docker server.

Do this once:

```sh
    docker-machine create --driver virtualbox scimma
```

Do this after ever reboot:

```sh
    docker-machine start scimma
```


Do this, as root, every time that you run a new shell (open a new window) in which you want to run docker commands associated with the scimma containers:

```
        eval $(docker-machine env scimma)
```

You can run ``docker-machine env dev`` on the command line to see what would be eavluated.

## WIndows Specific Notes

Tested on a Windows 10 Pro machine with [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10) installed.

In essence, a fairly vanilla installation of WSL and Docker Desktop (Community Edition of Docker is fine), as described [in this article](https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly) will suffice (although it may require the odd reboot). 

In essence, the Docker server runs on the Windows side under Hyper-V and the Docker client is on the Linux side and connects to the Docker server side via setting the `$DOCKER_HOST` environment variable. As soon as you can connect to the Docker server, for example with `docker ps`, you can run all the instructions above in WSL. 

**Note 1** Using [ConEmu](https://conemu.github.io/) or another tabbed console makes the "Extra Credit" section rather more convenient (and is recommended in any case, to get away from the limited console which ships with Windows).

**Note 2** WSL 2, currently available in Insider Windows builds, should allow Docker to be run entirely on the WSL/Linux side. For details on installation, see [this article](https://docs.microsoft.com/en-us/windows/wsl/wsl2-install)



## Linux Specific Notes

There were no issues running the above commands.

## TO DO

The plan is, as server and client code is written, to add the client code to the scimma client container and the server code to the scimma server container.
