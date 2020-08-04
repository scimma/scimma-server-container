import TestUtils as tu
import multiprocessing
import subprocess
import time
import os

messagesFile   = "data/stringMessages.txt"

def testTag():
    tag = os.environ.get('SCIMMA_TEST_TAG')
    if tag == None:
        tag = "latest"
    return tag

def clientImage (tag):
    return "scimma/client:%s" % tag

def serverImage (tag):
    return "scimma/server:%s" % tag

def startNet (net):
    print("Starting network: %s" % net)
    command = "docker network create %s" % net
    print("COMMAND: %s" % command)
    return os.system(command)

def stopNet (net):
    print("Stopping network: %s" % net)
    command = "docker network rm %s" % net
    print("COMMAND: %s" % command)
    return os.system(command)

class ServerContainer (multiprocessing.Process):

    def __init__ (self, tag, name="scimma-tst-srv", net="scimma-test", opts=[], dbg=False):
        super(ServerContainer,self).__init__(name=name)
        self.tag     = tag
        self.cimage  = tu.clientImage(tag)
        self.simage  = tu.serverImage(tag)
        self.name    = name
        self.options = opts
        self.network = net
        self.q       = multiprocessing.Queue()
        
        self.cmd  = "docker"
        self.args = ["run", "--detach=true", "--rm=true", "--network=%s" % net, "-v",
                     "shared:/root/shared", "--name=%s" % name] + opts + [self.simage];

    def run (self):
        print("starting server..")
        print("COMMAND: %s" % " ".join([self.cmd] + self.args))
        child = subprocess.Popen([self.cmd] + self.args)
        child.wait()

    def ipAddr (self):
        format = "'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'"
        cmd = "docker inspect --format=%s %s" % (format, self.name)
        line = subprocess.Popen([cmd], shell=True,
                                stdout=subprocess.PIPE).stdout.read().decode().splitlines()[0]
        return line.rstrip()

    def runClientCommand (self, cmd, opts=[]):
        command  = "docker run -i -v shared:/root/shared --rm=true --network=%s" % self.network
        command += " %s %s %s </dev/null" %  (" ".join(opts), self.cimage, cmd)
        print("COMMAND: %s" % command)
        os.environ["XDG_CONFIG_HOME"] = "/root"
        return os.system(command)

    def runClientCommandFileInput (self, cmd, fname, opts=[]):
        command  = "docker run -i -v shared:/root/shared --rm=true --network=%s " % self.network
        command += " %s %s %s <%s" %  (" ".join(opts), self.cimage, cmd, fname)
        print("COMMAND: %s" % command)
        return os.system(command)

    def runClientCommandWithOutput(self, cmd, opts=[]):
        command  = "docker run -i -v shared:/root/shared --rm=true --network=%s " % self.network
        command += " %s %s %s </dev/null" %  (" ".join(opts), self.cimage, cmd)
        print("COMMAND: %s" % command)
        return subprocess.Popen([command], shell=True, 
                                stdout=subprocess.PIPE).stdout.read().decode().splitlines()

    ##
    ## Loop at most tries times. Return true if we can talk to the server, false otherwise.
    ## Each try times out after 5 seconds. Wait a second between tries.
    def kafkaIsRunning (self, tries=10):
        command = "nc %s 9092 -w 5" % self.name
        n = tries
        while n > 0:
            n = n - 1
            if self.runClientCommand(command) == 0:
                  return True
            time.sleep(5*(tries - n))
        return False

    def terminate (self):
        os.system("docker kill %s " % self.name)

    def brokerString (self):
        return "%s:9092" % self.name
        
