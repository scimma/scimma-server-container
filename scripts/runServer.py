#!/usr/bin/python3
from optparse        import OptionParser
from multiprocessing import Process
import os
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
parser.add_option("", "--brokerUser",   dest="brokerUser",   default="admin"))
parser.add_option("", "--brokerPass",   dest="brokerPass",   default="admin-secret"))
parser.add_option("", "--users",        dest="usersList",    default="test:test-pass")
parser.add_option("", "--noSecurity",   dest="noSec",        default=False, action="store_true")
parser.add_option("", "--javaDebugSSL", dest="javaDebugSSL", default=False, action="store_true") 
(o, a) = parser.parse_args()

##
## Write SSL, kafka, and kafkacat configuration files.
##
config = ks.Config(o.javaDebugSSL, o.noSec, o.keyPass, o.userList, o.brokerUser, o.brokerPass))
config.write()

##
## Set signal handlers.
##
sig.signal(sig.SIGTERM, ks.handleTermSig)
sig.signal(sig.SIGINT,  ks.handleTermSig)
sig.signal(sig.SIGHUP,  ks.ignoreSig)
sig.signal(sig.SIGSEGV, ks.ignoreSig)
sig.signal(sig.SIGABRT, ks.ignoreSig)
sig.signal(sig.SIGBUS,  ks.ignoreSig)
sig.signal(sig.SIGFPE,  ks.ignoreSig)
sig.signal(sig.SIGPIPE, ks.ignoreSig)
sig.signal(sig.SIGALRM, ks.ignoreSig)

##
## Run kafka and zookeeper processes.
##
kc = ks.command('kafka','/usr/bin/kafka-server-start  /etc/kafka/server.properties',    '/tmp')
zc = ks.command('zk','/usr/bin/zookeeper-server-start /etc/kafka/zookeeper.properties', '/tmp')
processes = [Process(target=ks.runCommand, args=(kc)), Process(target=ks.runCommand, args=(zc))]
while True:
    sleep(1)
    if ks.Terminate:
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
exit(0)
