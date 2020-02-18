import socket
import Names
class Config:

    def __init__ (self, jDbg=False, noSec=False, passwd='123456'):
        self.jDbg   = jDbg
        self.noSec  = nosec
        self.passwd = passwd
        self.kcConfig     = "/root/shared/kafkacat.conf"
        self.kcTemplate   = "/etc/kafka/server.properties.auth"
        self.kcTemplateNA = "/etc/kafka/server.properties.no_auth"
        self.kConfig      = "/etc/kafka/server.properties"
        self.krc          = "/usr/bin/kafka-run-class"
        self.krcDbg       = "/usr/bin/kafka-run-class.java_debug"
        self.sslLog       = "/var/log/configureSSL.log"

    def write (self):
       self.writeSSLConfig()
       self.writeKafkacatConfig()
       self.writeKafkaConfig()

    def writeSSLConfig(self):
        names = Names.getHostnames()
        name = names[0]
        san = ",".join(map(lambda x: "dns:" + x, names))
        print("SSL KEY NAME: %s" % name)
        print("SSK KEY SAN:  %s" % san)
        os.system('mkdir -p /root/shared/tls')
        os.chdir('/root/shared/tls')
        # Generate key.
        runSSLComamnd(("keytool -keystore kafka.server.keystore.jks -alias localhost -validity 365 "
                      "-genkey -keyalg RSA -keypass %s -storepass %s -storetype pkcs12 -dname "
                      "cn=%s, ou=scimma-test, o=scimma-test, c=US\" -ext %s 2>&1")
                      % (self.passwd, self.passwd, name, san)
        # Create CA
        runSSLCommand(("openssl req -new -x509 -keyout ca-key -out ca-cert -days 365 -passout pass:%s "
                      "-subj \"/C=US/postalCode=00000/ST=Pennsylvania/L=Test/O=Test/OU=Test/CN=test-ca\" "
                      "2>&1") % self.passwd)
        # Import root cert into a server and client truststore.
        runSSLCommand(("keytool -keystore kafka.client.truststore.jks -alias CARoot -importcert -file "
                      "ca-cert -storepass %s -storetype pkcs12 -noprompt 2>&1") % self.passwd)
        runSSLCommand(("keytool -keystore kafka.server.truststore.jks -alias CARoot -importcert -file "
                      "ca-cert -storepass %s -storetype pkcs12 -noprompt 2>&1") % self.passwd)
        # Generate a request.
        runSSLCommand(("keytool -keystore kafka.server.keystore.jks -alias localhost -certreq -file "
                      "cert-file -storepass %s 2>&1") % self.passwd)
        # Sign the request.                      
        runSSLCommand(("openssl x509 -req -CA ca-cert -CAkey ca-key -in cert-file -out cert-signed "
                      "-days 365 -CAcreateserial -passin pass:%s 2>&1") % self.passwd)
        # Import the signed request and the server key into the server's keystore.
        runSSLCommand(("keytool -keystore kafka.server.keystore.jks -alias CARoot -import -file "
                       "ca-cert -storepass %s -noprompt 2>&1") % self.passwd)
        runSSLCommand(("keytool -keystore kafka.server.keystore.jks -alias localhost -import "
                       "-file cert-signed -storepass %s 2>&1") % sef.passwd)
        # Export CA cert
        runSSLCommand(("keytool -keystore kafka.client.truststore.jks -exportcert -alias caroot "
                       "-storepass %s | openssl x509 -inform DER > cacert.pem") % self.passwd)

    def runSSLCommand (cmd):
        hr = "==========================================================\n";
        f = open(self.sslLog, "a+")
        f.write(hr)
        f.write("COMMAND: " + cmd + "\nOUT:\n")
        lines = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE).stdout.read().decode()
        f.write(lines)
        f.close()
