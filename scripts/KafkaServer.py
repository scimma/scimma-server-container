import socket
import multiprocessing
import os
import time

Terminate = False

def handleTermSig (num)
    print("Recieved SIGTERM. Exiting")
    Terminate = True

def ignoreSig (num)
    print("Recieved signal %d. Ignoring." % num)

def getHostnames ():
    cmd   = "ip -4 -o address"
    lines = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE).stdout.read().decode().splitlines()
    names = []
    for line in lines:
        ipm = re.match(r'\S+\s+\S+\s+inet\s+([0-9\.]+)\/', line)
        if ipm != None:
            names.extend(namesForAddress(ipm.group(1)))
    retNames = []
    for name in list(set(names)):
        um = re.match(r'^([a-zA-Z0-9\-\.]+)$', name)
        if um != None:
            retNames.append(name)
    return retNames

def namesForAddress (addr):
    name = socket.getfqdn(addr)
    names = [name]
    nm = re.match(r'^([^\.]+)\.(.+)$', name)
    if nm != None:
        names.append(nm.group(1))
    return names

def runCommand (cmd):
    numStarts  = 0
    while True:
        numStar = numStar + 1
        oLog = "/var/log/%s.out.%d" % cmd.name
        eLog = "/var/log/%s.err.%d" % cmd.name
        os.system("cd %s && (%s > %s 2 > %s)" % (cmd.wdir, cmd.cmd, oLog, eLog))
        time.sleep(5)
    
class Command:
        
    def __init__ (self, name, cmd, wdir):
        self.name = name
        self.cmd  = cmd
        self.wdir = wdir

class Config:

    kcConfig     = "/root/shared/kafkacat.conf"
    kcTemplate   = "/etc/kafka/server.properties.auth"
    kcTemplateNA = "/etc/kafka/server.properties.no_auth"
    kConfig      = "/etc/kafka/server.properties"
    krc          = "/usr/bin/kafka-run-class"
    krcDbg       = "/usr/bin/kafka-run-class.java_debug"
    sslLog       = "/var/log/configureSSL.log"
    tlsDir       = "/root/shared/tls"

    def __init__ (self, jDbg=False, noSec=False, pwd='123456', ul='test:test-pass', bu='admin', \
                  bp='admin-secret'):
        self.jDbg   = jDbg
        self.noSec  = nosec
        self.pwd    = pwd
        self.ul     = ul
        self.bu     = bu
        self.bp     = bp

    def write (self):
       self.writeSSLConfig()
       self.writeKafkacatConfig()
       self.writeKafkaConfig()
       if self.jDbb:
           os.sytem("cp %s %s" % self.krcDbg, self.krc)

    def writeSSLConfig(self):
        names = getHostnames()
        name = names[0]
        san = ",".join(map(lambda x: "dns:" + x, names))
        print("SSL KEY NAME: %s" % name)
        print("SSK KEY SAN:  %s" % san)
        os.system("mkdir -p " + self.tlsDir)
        os.chdir(self.tlsDir)
        # Generate key.
        self.runSSLComamnd(("keytool -keystore kafka.server.keystore.jks -alias localhost -validity 365 "
                      "-genkey -keyalg RSA -keypass %s -storepass %s -storetype pkcs12 -dname "
                      "cn=%s, ou=scimma-test, o=scimma-test, c=US\" -ext %s 2>&1")
                      % (self.pwd, self.pwd, name, san)
        # Create CA
        self.runSSLCommand(("openssl req -new -x509 -keyout ca-key -out ca-cert -days 365 -passout pass:%s "
                      "-subj \"/C=US/postalCode=00000/ST=Pennsylvania/L=Test/O=Test/OU=Test/CN=test-ca\" "
                      "2>&1") % self.pwd)
        # Import root cert into a server and client truststore.
        self.runSSLCommand(("keytool -keystore kafka.client.truststore.jks -alias CARoot -importcert -file "
                      "ca-cert -storepass %s -storetype pkcs12 -noprompt 2>&1") % self.pwd)
        self.runSSLCommand(("keytool -keystore kafka.server.truststore.jks -alias CARoot -importcert -file "
                      "ca-cert -storepass %s -storetype pkcs12 -noprompt 2>&1") % self.pwd)
        # Generate a request.
        self.runSSLCommand(("keytool -keystore kafka.server.keystore.jks -alias localhost -certreq -file "
                      "cert-file -storepass %s 2>&1") % self.pwd)
        # Sign the request.                      
        self.runSSLCommand(("openssl x509 -req -CA ca-cert -CAkey ca-key -in cert-file -out cert-signed "
                      "-days 365 -CAcreateserial -passin pass:%s 2>&1") % self.pwd)
        # Import the signed request and the server key into the server's keystore.
        self.runSSLCommand(("keytool -keystore kafka.server.keystore.jks -alias CARoot -import -file "
                       "ca-cert -storepass %s -noprompt 2>&1") % self.pwd)
        self.runSSLCommand(("keytool -keystore kafka.server.keystore.jks -alias localhost -import "
                       "-file cert-signed -storepass %s 2>&1") % sef.passwd)
        # Export CA cert
        self.runSSLCommand(("keytool -keystore kafka.client.truststore.jks -exportcert -alias caroot "
                       "-storepass %s | openssl x509 -inform DER > cacert.pem") % self.pwd)

    def runSSLCommand (self, cmd):
        hr = "==========================================================\n";
        f = open(self.sslLog, "a+")
        f.write(hr)
        f.write("COMMAND: " + cmd + "\nOUT:\n")
        lines = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE).stdout.read().decode()
        f.write(lines)
        f.close()

    def writeKafkacatConfig (self):
        f = open(kcConfig, "w")
        if not self.noSec:
            f.write(("ssl.ca.location=%s/cacert.pem\nsecurity.protocol=SASL_SSL\n"
                     "sasl.mechanism=PLAIN\nsasl.username=%s\nsasl.password="
                     "%s") % tuple([self.tlsDir].extend(self.ul.split(',')[0].split(':')))
        f.close()

    def writeKafkaConfig (self):
        kcOut  = open(kcConfig, "w")
        uCreds = "\n".join(map(lambda x: "sasl.username=%s\nsasl.password=%s" % tuple(x.split(':')), 
                               self.ul))
        keyCertPasswrods = ("ssl.truststore.password=%s\nssl.keystore.password=%s\nssl.key.password="
                            "%s\n") % (self.pwd, self.pwd, self.pwd)
        if self.noSec:
            kcIn = open(kcTemplateNA, "r")
            while True:
                line = kcIn.readline()
                if line == ''
                    kcIn.close()
                    break
                kcOut.write(line)
        else:
            kcIn = open(kcTemplate, "r")
            while True:
                line = kcIn.readline()
                if line == ''
                    kcIn.close()
                    break
                re.compile('KAFKA_CREDENTIALS').sub(uCreds, line)
                re.compile('SSL_KEY_CERT_PASSWORDS').sub(keyCertPasswords, line)
                kcOut.write(line)
        kcOut.close()
