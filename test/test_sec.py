import TestUtils as tu
import re

def setup_module (module):
    global server
    tu.startNet("scimma-test")
    server = tu.ServerContainer(tu.testTag(), opts=["-v", "shared:/root/shared"])
    server.start()

def teardown_module (module):
    server.terminate()
    tu.stopNet("scimma-test")

def test_kafkaRunning ():
    assert(server.kafkaIsRunning())

def test_expectedListenIP ():
    expected = "broker 0 at %s:9092" % server.ipAddr()
    print("expected: \"%s\"" % expected)
    command  = "kafkacat -L -b %s" % server.brokerString()
    lines    = server.runClientCommandWithOutput(command)
    matched  = False
    for line in lines:
        print("matching line: \"%s\"" % line)
        if line.find(expected) > -1:
            matched = True
            break
    assert(matched)

def test_publish ():
    command = "kafkacat -P -b %s -t test" % server.brokerString()
    assert(server.runClientCommandFileInput(command, tu.messagesFile) == 0)

def test_consume ():
    command = "kafkacat -C -b %s -t test -e" % server.brokerString()
    lines = server.runClientCommandWithOutput(command)
    fh = open(tu.messagesFile, "r")
    flines = map(lambda x: x.strip(), fh.readlines())
    fh.close()
    print("lines:\n%s\n" %  "\n".join(lines))
    print("=========")
    print("flines:\n%s\n" % "\n".join(flines))
    plist = zip(lines, flines)
    result = True
    for p in plist:
        if p[0] != p[1]:
            result = False
    assert(result == True)

def test_failIfNoClientSSL ():
    command = "kafkacat -F /dev/null -L -b %s " % server.brokerString()
    assert(server.runClientCommand(command) != 0)

def test_failIfSslAndBadPasswd ():
    extraArgs  = "-X ssl.ca.location=/root/shared/tls/cacert.pem -X security.protocol=SASL_SSL -X "
    extraArgs += "sasl.mechanism=PLAIN -X sasl.username=test -X sasl.password=foo"
    command = "kafkacat -F /dev/null -L %s -b %s " % (extraArgs, server.brokerString())
    assert(server.runClientCommand(command) != 0)

def test_okIfSslAndGoodPasswd ():
    extraArgs  = "-X ssl.ca.location=/root/shared/tls/cacert.pem -X security.protocol=SASL_SSL -X "
    extraArgs += "sasl.mechanism=PLAIN -X sasl.username=test -X sasl.password=test-pass"
    command = "kafkacat -F /dev/null -L %s -b %s " % (extraArgs, server.brokerString())
    assert(server.runClientCommand(command) == 0)

# def test_scimmaPublishGCN ():
#     brk = "kafka://%s/gcn" % server.brokerString()
#     gcn = "/root/test_data/example.gcn3"
#     command = "hop publish --no-auth %s %s" % (brk, gcn)
#     assert(server.runClientCommand(command) == 0)

# def test_scimmaSubscribeGCN ():
#     brk = "kafka://%s/gcn" % server.brokerString()
#     command = "hop subscribe --no-auth -s EARLIEST %s" % (brk)
#     assert(server.runClientCommand(command) == 0)
