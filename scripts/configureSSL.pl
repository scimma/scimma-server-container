#!/usr/bin/perl -w
###
### This script creates the following files in the directory /root/tls (which is
### created if it does not exist):
###
###      a-cert
###      ca-cert.srl
###      ca-key
###      cert-file
###      cert-signed
###      kafka.client.truststore.jks
###      kafka.server.keystore.jks
###      kafka.server.truststore.jks
###
###
use strict;

##
## Password for truststore/keystore
##
my($pw) = $ARGV[0];
if (!defined($pw)) {
    $pw = '123456';
}

my(@altNames) = getHostnames();
my($name)     = `hostname`;
chomp($name);
push(@altNames, $name);

my($n);
my(@sanEntries);
for $n (@altNames) {
    push(@sanEntries, sprintf("dns:%s", $n));
}
my($san) = "san=" . join(",", @sanEntries);

# Create a directory to store our output files.
`mkdir -p /root/shared/tls`;
chdir('/root/shared/tls');
`cd /root/shared/tls && find . -type f | xargs rm -f`;

# Generate key.
printf("SSL KEY NAME: %s\n", $name);
printf("SSK KEY SAN:  %s\n", $san);
system(sprintf("keytool -keystore kafka.server.keystore.jks -alias localhost -validity 365 -genkey -keypass %s -storepass %s -storetype pkcs12 -dname \"cn=%s, ou=scimma-test, o=scimma-test, c=US\" -ext %s >/dev/null 2>/dev/null",
                   $pw, $pw, $name, $san));
# Create CA
system(sprintf("openssl req -new -x509 -keyout ca-key -out ca-cert -days 365 -passout pass:%s -subj \"/C=US/postalCode=00000/ST=Pennsylvania/L=Test/O=Test/OU=Test/CN=test-ca\" >/dev/null 2>/dev/null", $pw));

# Import root cert into a server and client truststore.
system("keytool -keystore kafka.client.truststore.jks -alias CARoot -importcert -file ca-cert -storepass $pw -storetype pkcs12 -noprompt >/dev/null 2>/dev/null");
system("keytool -keystore kafka.server.truststore.jks -alias CARoot -importcert -file ca-cert -storepass $pw -storetype pkcs12 -noprompt >/dev/null 2>/dev/null");

# Generate a request.
system("keytool -keystore kafka.server.keystore.jks -alias localhost -certreq -file cert-file -storepass $pw >/dev/null 2>/dev/null");

# Sign the request.
system("openssl x509 -req -CA ca-cert -CAkey ca-key -in cert-file -out cert-signed -days 365 -CAcreateserial -passin pass:$pw >/dev/null 2>/dev/null");

# Import the signed request and the server key into the server's keystore.
system("keytool -keystore kafka.server.keystore.jks -alias CARoot    -import -file ca-cert -storepass $pw -noprompt >/dev/null 2>/dev/null");
system("keytool -keystore kafka.server.keystore.jks -alias localhost -import -file cert-signed -storepass $pw >/dev/null 2>/dev/null");

# Export CA cert
system("keytool -keystore kafka.client.truststore.jks -exportcert -alias caroot  -storepass $pw | openssl x509 -inform DER > cacert.pem");

exit(0);

sub getHostnames {
    my(@ipOut) = `ip -4 -o address`;
    my($line);
    my(@names);
    for $line (@ipOut) {
        chomp($line);
        if ($line =~ /^\S+\s+\S+\s+inet\s+([0-9\.]+)\//) {
            push(@names, namesForAddress($1));
        }
    }
    return @names;
}

sub namesForAddress {
    my($addr) = shift;
    my($nslookupCommand) = sprintf("nslookup %s", $addr);
    my(@nslookupOut) = `$nslookupCommand`;
    my($line);
    my($name);
    for $line(@nslookupOut) {
        if ($line =~ /name = (\S+)\.\s*$/) {
            $name = $1;
        }
        last;
    }
    my(@names);
    if ($name =~ /^([^\.]+)\.(.+)$/) {
        push(@names, $1);
    }
    push(@names, $name);
    return @names;
}
