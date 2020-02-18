#!/usr/bin/python3
from optparse import OptionParser
import os
import signal as sig
import MyUtils as mu
import Config as conf
import KafkaRunner
import ZookeeperRunner

parser = OptionParser()
parser.add_option("", "--help", dest="opt_help", action="count")
parser.add_option("", "--brokerUser", dest="opt_brokerUser", action="")

##
## Parse options
##

##
## Configure SSL
##

##
## Set signal handlers
##
# sig.signal(SIGNUM, handler)

