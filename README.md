## SCIMMA Server Container

The SCIMMA Server Container provides a development version of the SCIMMA server infrastructure which includes:

    1. A Kafka server.
    2. A Zookeeper installation used by the Kafka server
    3. SCIMMA server processes that consume and produce Kafka messages.

## Quick start (for the impatient)

Spin up a Kafka server listening on `localhost:9092`, with auth and config files accessible in `/tmp/shared`:

```
docker pull scimma/server:latest
docker run -p 9092:9092 -it --rm -v /tmp/shared:/root/shared --hostname localhost scimma/server
```

## Prerequisites:

  0. VirtualBox (Mac Only)
  1. Build tools: GNU Make, curl, git (only if building the containers)
  2. Working docker installation

## Use Cases

Documentation for basic use cases:

 1. [SCIMMA client development](doc/ClientDevelopment.md)
 2. [Quick Demo/Script](doc/QuickDemo.md)
 3. [Connect to dev HOPSKOTCH](doc/HopskotchDev.md)

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

## Build

```
make
```

## Release

Pushing to hub.docker.com is handled via a github workflow. To push a container based on
the current master branch to AWS ECR with
version MAJOR.MINOR.RELEASE (e.g., "0.0.7") do:

```
git tag version-MAJOR.MINOR.RELEASE
git push origin version-MAJOR.MINOR.RELEASE
```

## OS Specific Notes

We have tested the containers using several combinations of operating systems and docker installations here are some notes about running the demo in various environments:

  1. [Windows](doc/Windows.md)
  2. [Mac - macports](doc/Mac-macports.md)
  3. [Linux](doc/Linux.md)

## TO DO

The plan is, as server and client code is written, to add the client code to the scimma client container and the server code to the scimma server container.
