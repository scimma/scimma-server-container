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
use FileHandle;
use Socket;

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

## For keytool, names must consist of: leters, digits, and hyphens
my(@tmpNames);
for $name (@altNames) {
    if (!($name =~ /^[a-zA-Z0-9\-]+$/)) {
    printf("Excluding name from SAN: %s\n", $name);
    next;
    }
    push(@tmpNames, $name);
}
@altNames = @tmpNames;

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

my($command);

my($sclog) = "/var/log/configureSSL.log";
my($scfh) = FileHandle->new($sclog, "w");
# Generate key.
printf("SSL KEY NAME: %s\n", $name);
printf("SSK KEY SAN:  %s\n", $san);
runSSLCommand(sprintf("keytool -keystore kafka.server.keystore.jks -alias localhost -validity 365 -genkey -keypass %s -storepass %s -storetype pkcs12 -dname \"cn=%s, ou=scimma-test, o=scimma-test, c=US\" -ext %s 2>&1", $pw, $pw, $name, $san), $scfh);

# Create CA
runSSLCommand(sprintf("openssl req -new -x509 -keyout ca-key -out ca-cert -days 365 -passout pass:%s -subj \"/C=US/postalCode=00000/ST=Pennsylvania/L=Test/O=Test/OU=Test/CN=test-ca\" 2>&1", $pw), $scfh);

# Import root cert into a server and client truststore.
runSSLCommand("keytool -keystore kafka.client.truststore.jks -alias CARoot -importcert -file ca-cert -storepass $pw -storetype pkcs12 -noprompt 2>&1", $scfh);

runSSLCommand("keytool -keystore kafka.server.truststore.jks -alias CARoot -importcert -file ca-cert -storepass $pw -storetype pkcs12 -noprompt 2>&1", $scfh);

# Generate a request.
runSSLCommand("keytool -keystore kafka.server.keystore.jks -alias localhost -certreq -file cert-file -storepass $pw 2>&1", $scfh);

# Sign the request.
runSSLCommand("openssl x509 -req -CA ca-cert -CAkey ca-key -in cert-file -out cert-signed -days 365 -CAcreateserial -passin pass:$pw 2>&1", $scfh);

# Import the signed request and the server key into the server's keystore.
runSSLCommand("keytool -keystore kafka.server.keystore.jks -alias CARoot    -import -file ca-cert -storepass $pw -noprompt 2>&1", $scfh);
runSSLCommand("keytool -keystore kafka.server.keystore.jks -alias localhost -import -file cert-signed -storepass $pw 2>&1", $scfh);

# Export CA cert
runSSLCommand("keytool -keystore kafka.client.truststore.jks -exportcert -alias caroot  -storepass $pw | openssl x509 -inform DER > cacert.pem", $scfh);

$scfh->close();

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
    if (!defined($name)) {
        #Address has no associated DNS name
        #Try gethostbyaddr
        $name = gethostbyaddr(inet_aton($addr), AF_INET);
        if (!defined($name)) {
            return ();
        }
    }
    my(@names);
    if ($name =~ /^([^\.]+)\.(.+)$/) {
        push(@names, $1);
    }
    push(@names, $name);
    return @names;
}

sub runSSLCommand {
    my($command) = shift;
    my($fh)      = shift;
    my($hr) = "==========================================================\n";
    printf($fh $hr);
    printf($fh "COMMAND: %s\nOUT:\n", $command);
    my(@out) = `$command`;
    print $fh @out;
}
