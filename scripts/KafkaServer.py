import multiprocessing
import subprocess
import socket
import time
import re
import os
import sys
import signal as sig

import toml

def getHostnames ():
    cmd   = "ip -4 -o address"
    lines = subprocess.Popen([cmd], shell=True,
                             stdout=subprocess.PIPE).stdout.read().decode().splitlines()
    names = []
    for line in lines:
        ipm = re.match(r'\S+\s+\S+\s+inet\s+([0-9\.]+)\/', line)
        if ipm != None:
            names.extend(namesForAddress(ipm.group(1)))
    return list(filter(lambda x: re.match(r'^([a-zA-Z0-9\-\.]+)$', x) != None, list(set(names))))

def namesForAddress (addr):
    name = socket.getfqdn(addr)
    names = [name]
    nm = re.match(r'^([^\.]+)\.(.+)$', name)
    if nm != None:
        names.append(nm.group(1))
    lines = subprocess.Popen(["nslookup " + addr], shell=True,
                             stdout=subprocess.PIPE).stdout.read().decode().splitlines()    
    line = lines[0]
    nm = re.match(r'^\S+\s+name\s+=\s+(\S+)\.', line)
    if nm != None:
        name = nm.group(1)
        names.append(name)
        nm = re.match(r'^([^\.]+)\.(.+)$', name)
        if nm != None:
            names.append(nm.group(1))
    return list(set(names))

class Command(multiprocessing.Process):
        
    def __init__ (self, name, prog, args, wdir):
        super(Command,self).__init__(name=name)
        self.q         = multiprocessing.Queue()
        self.cmd       = prog
        self.wdir      = wdir
        self.args      = args
        self.count     = 0
        self.Terminate = False

    def run(self):
        while not self.Terminate:
            self.count = self.count + 1
            fo = open("/var/log/%s.out.%d" % (self.name, self.count), "w")
            fe = open("/var/log/%s.err.%d" % (self.name, self.count), "w")
            child = subprocess.Popen([self.cmd] + self.args, cwd=self.wdir, stdout=fo, stderr=fe)
            self.q.put(child.pid, False)
            try:
                child.wait()
            except KeyboardInterrupt:
                self.Terminate = 1
                print("Command.run %s: KeyboardInterrupt" % self.name)
            except:
                print("Command.run %s: child.wait unexpected exception" % self.name)
            else:
                print("Command.run %s: child.wait normal exit." % self.name)
            fo.close()
            fe.close()
            time.sleep(5)
        print("Command.run %s: exiting." % self.name)

    def JustDieAlready(self):
        self.Terminate = True
        while not self.q.empty():
            pid = self.q.get()
            print("JustDieAlready %s: sending TERM to child: %d" % (self.name, pid))
            os.system("kill -TERM %d >/dev/null 2>/dev/null" % pid)
        print("JustDieAlready: %s: finished killing children." % self.name)
        self.terminate()

class Config:

    kcConfig     = "/root/shared/kafkacat.conf"
    hopConfig    = "/root/shared/config.toml"
    kcTemplate   = "/etc/kafka/server.properties.auth"
    kcTemplateNA = "/etc/kafka/server.properties.no_auth"
    kConfig      = "/etc/kafka/server.properties"
    krc          = "/usr/bin/kafka-run-class"
    krcDbg       = "/usr/bin/kafka-run-class.java_debug"
    sslLog       = "/var/log/configureSSL.log"
    tlsDir       = "/root/shared/tls"

    def __init__ (self, jDbg, noSec, pwd, ul, bu, bp, al):
        self.jDbg   = jDbg
        self.noSec  = noSec
        self.pwd    = pwd
        self.ul     = ul
        self.bu     = bu
        self.bp     = bp
        self.al     = al

    def write (self):
       self.writeSSLConfig()
       self.writeKafkacatConfig()
       self.writeHopConfig()
       self.writeKafkaConfig()
       if self.jDbg:
           os.system("cp %s %s" % (self.krcDbg, self.krc))

    def writeSSLConfig(self):
        names = getHostnames()
        name  = socket.gethostname()
        san   = ",".join(map(lambda x: "dns:" + x, names))
        print("SSL KEY NAME: %s" % name)
        print("SSK KEY SAN:  %s" % san)

        # Remove old SSL configuration files and prepare to run SSL commands.
        efs = ['ca-cert', 'cacert.pem', 'cert-file', 'cert-signed', 'kafka.client.truststore.jks',
               'ca-key', 'ca-cert.srl', 'kafka.server.keystore.jks', 'kafka.server.truststore.jks']
        for ef in efs:
            efp = "%s/%s" % (self.tlsDir, ef)
            os.system("if [ -f %s ]; then rm -f %s; fi" % (efp, efp))
        os.system("mkdir -p " + self.tlsDir)
        os.chdir(self.tlsDir)
        f = open(self.sslLog, "w")
        f.close()

        # Generate key.
        self.runSSLCommand("keytool -keystore kafka.server.keystore.jks -alias localhost -validity 365 "
                           "-genkey -keyalg RSA -keypass %s -storepass %s -storetype pkcs12 -dname \""
                           "cn=%s, ou=scimma-test, o=scimma-test, c=US\" -ext \"san=%s\" 2>&1"
                           % (self.pwd, self.pwd, name, san))
        # Create CA
        self.runSSLCommand("openssl req -new -x509 -keyout ca-key -out ca-cert -days 365 -passout pass:%s "
                           "-subj \"/C=US/postalCode=00000/ST=Pennsylvania/L=Test/O=Test/OU=Test/CN=test-ca\" "
                           "2>&1" % self.pwd)
        # Import root cert into a server and client truststore.
        self.runSSLCommand("keytool -keystore kafka.client.truststore.jks -alias CARoot -importcert -file "
                           "ca-cert -storepass %s -storetype pkcs12 -noprompt 2>&1" % self.pwd)
        self.runSSLCommand("keytool -keystore kafka.server.truststore.jks -alias CARoot -importcert -file "
                           "ca-cert -storepass %s -storetype pkcs12 -noprompt 2>&1" % self.pwd)
        # Generate a request.
        self.runSSLCommand("keytool -keystore kafka.server.keystore.jks -alias localhost -certreq -file "
                           "cert-file -storepass %s 2>&1" % self.pwd)
        # Sign the request.                      
        self.runSSLCommand("openssl x509 -req -CA ca-cert -CAkey ca-key -in cert-file -out cert-signed "
                           "-days 365 -CAcreateserial -passin pass:%s 2>&1" % self.pwd)
        # Import the signed request and the server key into the server's keystore.
        self.runSSLCommand("keytool -keystore kafka.server.keystore.jks -alias CARoot -import -file "
                           "ca-cert -storepass %s -noprompt 2>&1" % self.pwd)
        self.runSSLCommand("keytool -keystore kafka.server.keystore.jks -alias localhost -import "
                           "-file cert-signed -storepass %s 2>&1" % self.pwd)
        # Export CA cert
        self.runSSLCommand("keytool -keystore kafka.client.truststore.jks -exportcert -alias CARoot "
                           "-storepass %s | openssl x509 -inform DER > cacert.pem" % self.pwd)

    def runSSLCommand (self, cmd):
        f = open(self.sslLog, "a+")
        f.write("==========================================================\n"
                "COMMAND: " + cmd + "\nOUT:\n")
        lines = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE).stdout.read().decode()
        f.write(lines)
        f.close()

    def writeKafkacatConfig (self):
        if not self.noSec:
            with open(self.kcConfig, "w") as f:
                f.write("ssl.ca.location=%s/cacert.pem\nsecurity.protocol=SASL_SSL\n"
                        "sasl.mechanism=PLAIN\nsasl.username=%s\nsasl.password="
                        "%s\n" % tuple([self.tlsDir] + self.ul.split(',')[0].split(':')))

    def writeHopConfig (self):
        if not self.noSec:
            username, password = self.ul.split(',')[0].split(':')
            config = {
                "auth": {
                    "username": username,
                    "password": password,
                    "mechanism": "PLAIN",
                    "ssl_ca_location": self.tlsDir
                }
            }
            with open(self.hopConfig, "w") as f:
                toml.dump(config, f)

    def writeKafkaConfig (self):
        kcOut  = open(self.kConfig, "w")
        uCreds =  " username=\"%s\" \\\n password=\"%s\" \\\n" % (self.bu, self.bp) + \
                  " user_%s=\"%s\" \\\n" % (self.bu, self.bp) + \
                  " \\\n".join(map(lambda x: " user_%s=\"%s\"" % tuple(x.split(':')), self.ul.split(','))) + \
                  ";\n"
        keyCertPasswords = ("ssl.truststore.password=%s\nssl.keystore.password=%s\nssl.key.password="
                            "%s\n") % (self.pwd, self.pwd, self.pwd)
        addr = socket.gethostbyname(socket.getfqdn())
        alStr = None
        if (self.al != None):
            alStr = "advertised.listeners=%s" % self.al            
        if self.noSec:
            kcIn = open(self.kcTemplateNA, "r")
            if (alStr == None):
                alStr = "advertised.listeners=PLAINTEXT://%s:9092" % addr
            while True:
                line = kcIn.readline()
                if line == '':
                    kcIn.close()
                    break
                line = re.sub('(ADVERTISED_LISTENERS)', alStr, line)
                kcOut.write(line)
        else:
            kcIn = open(self.kcTemplate, "r")
            if (alStr == None):
                alStr = "advertised.listeners=SASL_SSL://%s:9092" % addr
            while True:
                line = kcIn.readline()
                if line == '':
                    kcIn.close()
                    break
                line = re.sub('(KAFKA_CREDENTIALS)', uCreds, line)
                line = re.sub('(SSL_KEY_CERT_PASSWORDS)', keyCertPasswords, line)
                line = re.sub('(ADVERTISED_LISTENERS)', alStr, line)
                kcOut.write(line)
        kcOut.close()
        print(alStr)
