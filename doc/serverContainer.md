# Server Container Details

For the packages installed, the best documentation is the [Dockerfile.server file itself](../Dockerfile.server).

## EntryPoint

The entrypoint of the scimma/server container is:


```
    /root/runServer
```

which is a Perl script that:

    1. Creates SSL Keys and Certificates
    2. Configures Kafka
    3. Creates a kafkacat config file
    4. Runs Zookeeper
    5. Runs Kafka

It takes serveral options:

```
    --brokerUser=BUSER
    --brokerPass=BPASS
    --users=USER:PASS,...
    --keyPass=KPASS
```

**BUSER** and **BPASS** are the username and password used for inter-broker communication. The defaults are BUSER=_admin_ and BPASS=_admin-secret_.

Additional usernames and password can be specified as comma separated pairs with the elements of the pair separated by colons. The default
is _test:test-pass_.

**KPASS** is used as the password for Java keystores and truststores and is generally not referenced by clients.

In addition to normal operation, ``runServer`` can be called with ``--help`` to provide a description of the options:

```
       docker run -it  scimma/server --help
```

## SSL Keys and Certificates

The runServer script calls:

```
    /root/configureSSL.pl
```

to configure SSL. This is a very short script that runs a few keytool and openssl commands
to generate:

    1. A key for the server with appropriate subject alt names
    2. A self-signed key that acts as a certificate authority
    3. A server keystore and truststore used by Kafka
    4. A client truststore that could potentially be used by clients
    5. A cacert.pem file that can be used by SSL clients to trust the certificate authority

All of these files are written in:

```
     /root/shared/tls
```

## Kafka Configuration

The main Kafka configuration file is:

```
     /etc/kafka/server.properties 
```

It contains configuration for the network interfaces and ports to listen on, passwords, and it references the SSL keys and certificates created by ``configureSSL.pl``.

## Kafka SSL/Auth Configuration

The ``server.properties`` file is dynamically generated from a template, but the SSL/Auth relevant configuration
will be similar to:

```
##
## Listen using SSL on port 9092, use SASL for authentication:
##
listeners=SASL_SSL://:9092

##
## Use PLAIN SASL (usernames/passwords):
##
sasl.enabled.mechanisms=PLAIN

##
## Use SSL and SASL authentication for inter-broker communication:
##
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=PLAIN

##
## When using PLAIN authentication with SASL, use the follwing usernames/passwords.
## These are the defaults.
##
listener.name.sasl_ssl.plain.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="admin" \
  password="admin-secret" \
  user_admin="admin-secret" \
  user_test="test-pass";
```

# Kafkacat config file

The kafkacat config file is written to:

```
     /root/shared/kafkacat.conf
```

The ``kafkacat.conf`` file is not very useful where it sits. However, the scimma/client container 
has a symbolic link:

```
    /root/.config/kafkacat.conf   ->     /root/shared/kafkacat.conf
```

If the server and client are started with a named volume like so (server first):

```
     -v shared:/root/shared
```

Then the kafkacat configuration symbolic link in the client container will point to the
kafkacat configuration file generated by ``runServer``. The kafkacat configuration file
looks like:

```
  sl.ca.location=/root/shared/tls/cacert.pem
  security.protocol=SASL_SSL
  sasl.mechanism=PLAIN
  sasl.username=test
  sasl.password=test-pass

```

When doing [client develpment on the host](ClientDevelopment.md), it might can be convenient to run docker with
a local directory mapped to ``/root/shared``:

```
       -v  /my/path:/root/shared
``

where ``/my/path`` is a directory on the host. The ``cacert.pem`` file would then be available for easy
reference by kafkacat running on the host.

Another alternative is to copy the ``cacert.pem`` file using ``docker cp``.

## Running kafka and zookeeper

The ``runServer`` script runs one instance each of kafka and zookeeper. Should they exit, they are restarted.