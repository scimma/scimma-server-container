# Client Container Details

For the packages installed, the best documentation is the [Dockerfile.client file itself](../Dockerfile.client).

## EntryPoint

There is no ``ENTRYPOINT`` defined for the scimma/client container. It only defines a ``CMD``. The purpose is
to allow the initial program that is run by docker run to be easily set on the command line. If you don't
override it, the initial program run is the value of ``CMD`` which is ``/bin/bash``.

One of the most useful commands for interacting with the scimma/client container is [kafkacat](https://github.com/edenhill/kafkacat).

## Kafkacat Configuration

The default file where kafkacat looks for configuration is ``${HOME}/.config/kafkacat.conf``. Since the processes inside the container are running as ``root``, kafkacat will look for configuration in the file ``/root/.config/kafkacat.conf``.

In the scimma/client container, ``/root/.config/kafkacat.conf`` is a symbolic link that points at ``/root/shared/kafkacat.conf`` which, by default, doesn't exist.

It is recommended that the server and client (server first) be started with the option:

```
  -v shared:/root/shared
```

When the scimma/server container is started with this option, it will create a *named* volume which will be accessible to other containers that use the same option. It will write the file ``/root/shared/kafkacat.conf`` which contains the information that kafkacat needs to connect to the server. It will typically look like:

```
ssl.ca.location=/root/shared/tls/cacert.pem
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.username=test
sasl.password=test-pass
```

Using the configuration file is equivalent to using the following flags on the kafkacat command line:

```
   -X ssl.ca.location=/root/shared/tls/cacert.pem -X security.protocol=SASL_SSL -X sasl.mechanism=PLAIN -X sasl.username=test -X sasl.password=test-pass
```

Note that the configuration file references ``/root/shared/tls/cacert.pem`` which is also on the named volume shared by the server container.

There may be times when you want use another configuration file or you want to make sure that the default configuration file is not used. The ``-F FILE`` option overrides the default configuration file. You can set ``FILE`` to your own configuration file or to ``/dev/null`` to make sure that no extra configuration is used by kafkacat.
