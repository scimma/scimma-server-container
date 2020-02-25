import TestUtils as tu

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
