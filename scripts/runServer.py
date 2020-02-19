#!/usr/bin/python3
from optparse        import OptionParser
from multiprocessing import Process, Value
import os
import time
import signal      as sig
import KafkaServer as ks

##
## Parse options.
##
jDbg              = False
noSec             = False
password          = '123456'
userList          = 'test:test-pass'
brokerUser        = 'admin'
brokerPassword    = 'admin-secret'
parser = OptionParser(usage="Usage: %prog [options]")
parser.add_option("", "--keyPass",      dest="keyPass",      default="123456")
parser.add_option("", "--brokerUser",   dest="brokerUser",   default="admin")
parser.add_option("", "--brokerPass",   dest="brokerPass",   default="admin-secret")
parser.add_option("", "--users",        dest="userList",     default="test:test-pass")
parser.add_option("", "--noSecurity",   dest="noSec",        default=False, action="store_true")
parser.add_option("", "--javaDebugSSL", dest="javaDebugSSL", default=False, action="store_true") 
(o, a) = parser.parse_args()

##
## Write SSL, kafka, and kafkacat configuration files.
##
config = ks.Config(o.javaDebugSSL, o.noSec, o.keyPass, o.userList, o.brokerUser, o.brokerPass)
config.write()


##
## Remove meta.properties file if it exists. This supports the case of persisting
## /tmp/kafka-logs using a volume external to the container. The meta.properties
## file contains the cluster.id which is automatically generated.
##
os.system("if [ -f /tmp/kafka-logs/meta.properties ]; then rm -f /tmp/kafka-logs/meta.properties; fi");
##
## Set signal handlers.
##
#sig.signal(sig.SIGTERM, ks.handleTermSig)
#sig.signal(sig.SIGINT,  ks.handleTermSig)

##
## Run kafka and zookeeper processes.
##
kc = ks.Command('kafka','/usr/bin/kafka-server-start  /etc/kafka/server.properties',    '/tmp')
zc = ks.Command('zk','/usr/bin/zookeeper-server-start /etc/kafka/zookeeper.properties', '/tmp')

processes = [Process(target=ks.runCommand, args=(kc,)), Process(target=ks.runCommand, args=(zc,))]
for p in processes:
     p.start()

while True:
    time.sleep(1)
    if ks.Terminate:
        print("runServer TERMINATING...: " + repr(ks.Terminate))
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
exit(0)
