## SCIMMA Server Container

The SCIMMA Server Container provides a development version of the SCIMMA serverinfrastructure which includes:

    1. A Kafka server.
    2. A Zookeeper installation used by the Kafka server
    3. SCIMMA server processes that consume and produce Kafka messages.

The SCIMMA Server Container is intended to be useful for:

    1. SCIMMA integration testing
    2. SCIMMA development 
    3. SCIMMA client (both producer and consumer) development

## Prerequisites:

        1. Operating system: Mac/Linux (on Windows, run in a Linux virtual machine).
        1. working docker
        2. working docker-compose
        3. git

## Download and Build:

```
   git clone git@github.com:scimma/scimma-server-container.git
   cd scimma-server-container
   make
```


## Running




