#!/usr/bin/python3
from optparse import OptionParser
import os
import time
import signal      as sig
import KafkaServer as ks

##
## Parse options.
##
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
## Run kafka and zookeeper processes.
##


cms = [ks.Command('kafka','/usr/bin/kafka-server-start',['/etc/kafka/server.properties'],'/tmp'),
       ks.Command('zk','/usr/bin/zookeeper-server-start',['/etc/kafka/zookeeper.properties'],'/tmp')]

cms[1].start()
print("Started zookeeper.")
time.sleep(1)
cms[0].start()
print("Started kafka.")

##
## Set signal handlers.
##
Terminate = False
def handleTermSig (num, foo):
     global cms
     global Terminate
     for c in cms:
          c.JustDieAlready()
     Terminate = True

sig.signal(sig.SIGTERM, handleTermSig)
sig.signal(sig.SIGINT,  handleTermSig)
print("Signal handlers installed.")

##
## Wait for our inevitable death.
##
while not Terminate:
    time.sleep(1)

print("runServer: Exited main loop.")
for c in cms:
     print("runServer joining: %s" % c.name)
     c.join()

print("runServer: Exiting.")
exit(0)
