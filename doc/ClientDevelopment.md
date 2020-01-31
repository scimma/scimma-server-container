## Client Development 

For SCIMMA client development, it is convenient to use the SCIMMA server container like so:

```sh
    docker run -p 9092:9092 --hostname localhost scimma/server

```

This will download and run an instance of scimma/server that listens to port 9092 on the localhost.

You can then point your client software at:

```sh
       localhost:9092
```

for development and testing.

## Notes:

The hostname of the server is sent to kafka clients and the clients use the hostname to resolve to an IP address *even if* they are already connected to the kafka server (for example, by directly using the localhost IP address). It is, therefore, necessary to set the hostname of the server to a string that the client can resolve.

In the case above, the server is listening on the host machine's localhost address so ``localhost`` is used as the hostname.

