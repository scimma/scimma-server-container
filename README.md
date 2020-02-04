## SCIMMA Server Container

The SCIMMA Server Container provides a development version of the SCIMMA server infrastructure which includes:

    1. A Kafka server.
    2. A Zookeeper installation used by the Kafka server
    3. SCIMMA server processes that consume and produce Kafka messages.

## Prerequisites:

  0. VirtualBox (Mac Only)
  1. Build tools: GNU Make, curl, git (only if building the containers)
  2. Working docker installation
  3. Working docker-compose installation

## Use Cases

Documentation for basic use cases:

 1. [SCIMMA client development](doc/ClientDevelopment.md)
 2. [Demonstration and manual testing](doc/Demo.md)

The SCIMMA Server Container is most definitely **NOT** an example of 
best practice kafka infrastructure implementation. These
containers are not intended for production use.

## Detailed Container Descriptions

 1. [scimma/server](doc/serverContainer.md)
 2. [scimma/client](doc/clientContainer.md)


## DockerHub

The containers are published on https://dockerhub.com:

    * https://hub.docker.com/r/scimma/server
    * https://hub.docker.com/r/scimma/client

and can be pulled with the commands:

``` sh
    docker pull scimma/server
    docker pull scimma/client

```

Without building, you can use the containers on dockerhub.com using the docker-compose.yml file in this repository or direct docker commands.

## Building

The code is stored on github.com. Clone the repository:

```
   git clone git@github.com:scimma/scimma-server-container.git
```

Build the containers using GNU make:

```
   cd scimma-server-container
   make
```

The make command will complain if the repository is not clean. The result of a successful build are two containers:

``` sh
    scimma/server:TAG
    scimma/client:TAG
```
and two corresponding tags:

``` sh
    scimma/server:latest
    scimma/client:latest
```

where TAG is the hash of the latest git commit. 

## OS Specific Notes

We have tested the containers using several combinations of operating systems and docker installations here are some notes about running the demo in various environments:

  1. [Windows](doc/Windows.md)
  2. [Mac - macports](doc/Mac-macports.md)
  3. [Linux](doc/Linux.md)

## TO DO

The plan is, as server and client code is written, to add the client code to the scimma client container and the server code to the scimma server container.
