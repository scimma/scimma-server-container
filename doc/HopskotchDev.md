# Connect to HOPSKOTCH Development Server

This page describes one way to use the client container to connect to the HOPSKOTCH development server (``dev.hop.scimma.org``; referred to as ``dev.hop`` below).

### Configuration

To connect to ``dev.hop``, ``kafkacat`` will need the following configuration items:

```
security.protocol=SASL_SSL
sasl.username=**SOME_USERNAME**
sasl.password=**SOME_PASSWORD**
sasl.mechanism=PLAIN
ssl.ca.location=/etc/pki/tls/certs/ca-bundle.trust.crt

```
