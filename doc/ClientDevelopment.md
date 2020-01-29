## Client Development 

For SCIMMA client development, it is convenient to use the SCIMMA server container like so:

```sh
    docker run -p 9092:9092 scimma/server

```

This will download and run an instance of scimma/server that listens to port 9092 on the localhost.

You can then point your client software at:

```sh
       localhost:9092
```

for development and testing.
