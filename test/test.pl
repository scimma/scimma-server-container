#!/usr/bin/env perl
###
### This is a simple set of integration tests for the scimma/server and scimma/client continers.
###
use warnings;
use strict;
use Getopt::Long;
use FileHandle;
use Digest::MD5;

my($opt_Help);
my($opt_Debug);
GetOptions("debug"  => \$opt_Debug);

my($debug) = defined($opt_Debug);

##
## Take a tag to test as a command line argument.
##
my($G_tag) = "latest";
if (defined($ARGV[0])) {
    $G_tag = $ARGV[0];
}

my($G_serverImage) = sprintf("scimma/server:%s", $G_tag);
my($G_clientImage) = sprintf("scimma/client:%s", $G_tag);
my($G_testNetwork) = 'scimma-test';
my($G_testServerName) = "scimma-test-srv";

##
## Tests are divided up in to three stages. Each stage must complete
## successfully before the following stages will be run.
##
my(@preTests);   # Tests before scimma/server container is started
my(@startTests); # Tests associated with starting scimma/server container
my(@postTests);  # Tests while scimma/server is running

###
### Define tests.
###
push(@preTests, [\&imageExists, $G_clientImage]);
push(@preTests, [\&imageExists, $G_serverImage]);

push(@startTests, [\&containerRunning, $G_testServerName]);

push(@postTests, [\&sendStringMessages, "data/stringMessages.txt"]);
push(@postTests, [\&recvStringMessages, "data/stringMessages.txt"]);

###
### the testing network.
###
my($result);
my($createNetworkCommand) = sprintf("docker network create %s 2>&1", $G_testNetwork);
$debug && printf("NETWORK CREATE COMMAND: %s\n", $createNetworkCommand);
if (!createTestNetwork()) {
    fatalError(-1, "Could not create test network.");
}
my($G_testNetworkCreated) = 1;


###
### Stage 0: Before the server container is started.
###
my($t, $tCount);
my($numPreTests) = scalar(@preTests);
my($numPreTestsSuccessful) = 0;
printf("Stage 0: Before Server Start. Tests: %d\n", $numPreTests);
$tCount = 0;
my($preTestSuccess) = 1;
my($state);
for $t (@preTests) {
    $tCount++;
    $state = runTest(0, $tCount, $numPreTests, $t);
    ($state) && ($numPreTestsSuccessful++);
    $preTestSuccess = $preTestSuccess * $state;
}
if (!$preTestSuccess) {
    fatalError(-2, "Stage 0: Some tests failed. Successful: [%d/%d]", $numPreTestsSuccessful, $numPreTests);
} else {
    printf("Stage 0: Success! [%d/%d]\n", $numPreTestsSuccessful, $numPreTests);
}
printf("\n");

##
## Stage 1: Start the scimma/server container.
##
my($scimmaServerStartCommand) = sprintf("docker run -p 9092:9092 --detach=true --rm=true --network=%s --name=%s %s", $G_testNetwork, $G_testServerName, $G_serverImage);
$debug && printf("SERVER START COMMAND: %s\n", $scimmaServerStartCommand);
my(@startServerOut) = `$scimmaServerStartCommand`;
if ($? != 0) {
    printf(STDERR "COMMAND: %s\n\n", $scimmaServerStartCommand);
    printf(STDERR "OUTPUT:\n");
    print(STDERR @startServerOut);
    printf("\n");
    fatalError(-2, "Could not start scimma-server container.");
}
my($G_testServerStarted) = 1;

printf("Stage 1: Starting test scimma/server container.\n");
my($numStartTests) = scalar(@startTests);
my($numStartTestsSuccessful) = 0;
my($startTestSuccess) = 1;
$tCount = 0;
for $t (@startTests) {
    $tCount++;
    $state = runTest(1, $tCount, $numStartTests, $t);
    ($state) && ($numStartTestsSuccessful++);
    $startTestSuccess = $startTestSuccess * $state;
}

if (!$startTestSuccess) {
    fatalError(-3, "Stage 1: Some tests failed. Successful: [%d/%d]", $numStartTestsSuccessful, $numStartTests);
} else {
    printf("Stage 1: Success! [%d/%d]\n", $numStartTestsSuccessful, $numStartTests);
}
printf("\n");
sleep(2);

###
### Stage 2: Server container is running.
###
printf("Stage 2: Server container is running.\n");
my($numPostTests) = scalar(@postTests);
my($numPostTestsSuccessful) = 0;
my($postTestSuccess) = 1;
$tCount = 0;
for $t (@postTests) {
    $tCount++;
    $state = runTest(2, $tCount, $numPostTests, $t);
    ($state) && ($numPostTestsSuccessful++);
    $postTestSuccess = $postTestSuccess * $state;
}

if (!$postTestSuccess) {
    fatalError(-4, "Stage 2: Some tests failed. Successful: [%d/%d].", $numPostTestsSuccessful, $numPostTests);
} else {
    printf("Stage 2: Success! [%d/%d]\n", $numPostTestsSuccessful, $numPostTests);
}
printf("\n");

cleanup();
exit(0);
###
### Not reached.
###
sub createTestNetwork {
    my(@out) = `$createNetworkCommand`;
    my($status) = $?;
    my($ok) = 0;
    if ($status != 0) {
        my($line) = $out[0];
        if ($line =~ /network with name scimma-test already exists/) {
            $ok = 1;
        }
    } else {
        $ok = 1;
    }
    return $ok;
}

sub fatalError {
    my($exitValue) = shift;
    my($msg)       = shift;
    printf(STDERR "Fatal: " . $msg . "\n", @_);
    printf(STDERR "Exiting.\n");
    cleanup();
    exit($exitValue);
}

###
### Run a test function. 
###
sub runTest {
    my($stage)    = shift;
    my($num)      = shift;
    my($tot)      = shift;
    my($testAref) = shift;

    my($test, @args) = @{$testAref};
    my(@ret)    = &$test(@args);
    my($passed) = $ret[0];
    my($name)   = $ret[1];

    my($passedString) = "OK";
    if (!$passed) {
        $passedString = "FAIL";
    }
    printf("[%d:%d/%d] %-60s ", $stage, $num, $tot, $name);
    printf("%s\n", $passedString);
    return $passed;
}

sub imageExists {
    my($image) = shift;
    my($command) = sprintf("docker image inspect %s >/dev/null 2>/dev/null", $image);
    `$command`;
    my($name) = sprintf("Image exists: %s", $image);
    if ($? == 0) {
        return (1, $name);
    } else {
        return (0, $name);
    }
}

sub countLines {
    my($fname) = shift;
    my($lcount) = 0;
    my($fh) = FileHandle->new($fname, "r");
    my($line);
    while ($line = <$fh>) {
        $lcount++;
    }
    $fh->close();
    return $lcount;
}

sub getLines {
    my($fname) = shift;
    my($fh) = FileHandle->new($fname, "r");
    my(@out);
    my($line);
    while ($line = <$fh>) {
        chomp($line);
        push(@out, $line);
    }
    $fh->close();
    return @out;
}

sub sendStringMessages {
    my($fname) = shift;
    my($command) = sprintf("cat %s | docker run  -i --network=%s -link=%s %s /usr/local/bin/kafkacat -P -b scimma-test-srv:9092 -t test",
                           $fname, $G_testNetwork, $G_testServerName, $G_clientImage);
    $debug && printf("SENDSTRINGMESSAGE COMMAND: %s\n", $command);
    my($numLines) = countLines($fname);
    my($name) = sprintf("Send %d lines as messages from file: %s", $numLines, $fname);
    my(@out) = `$command`;
    my($ec) = $?;
    if ($ec == 0) {
        return (1, $name);
    } else {
        return (0, $name);
    }
}

sub recvStringMessages {
    my($fname) = shift;
    my($numLines) = countLines($fname);
    my($command) = sprintf("docker run  -i --network=%s -link=%s %s /usr/local/bin/kafkacat -C -b scimma-test-srv:9092 -t test  -o -%d -e 2>/dev/null",
                           $G_testNetwork, $G_testServerName, $G_clientImage, $numLines);
    $debug && printf("RECVSTRINGMESSAGE COMMAND: %s\n", $command);
    my(@recvLines) = `$command`;
    chomp(@recvLines);

    my(@sentLines) = getLines($fname);

    my($name) = sprintf("Receive %d lines and compare to file: %s", $numLines, $fname);
    if (scalar(@recvLines) != scalar(@sentLines)) {
        return(0, $name);
    }
    my($badLines) = 0;
    my($i) = 0;
    for ($i=0; $i<$numLines; $i++) {
        if (!($sentLines[$i] eq $recvLines[$i])) {
            $badLines++;
        }
    }
    if ($badLines == 0) {
        return (1, $name);
    } else {
        return (0, $name);
    }
}

sub containerRunning {
    my($containerName) = shift;
    my($command) = sprintf("docker inspect --type=container %s", $containerName);
    my(@out) = `$command`;
    my($name) = sprintf("Container is running: %s", $containerName);
    if ($? == 0) {
        return (1, $name);
    } else {
        return (0, $name);
    }
}

sub cleanup {
    $debug && printf(STDERR "RUNNING CLEANUP...\n");
    if ($G_testServerStarted) {
        $debug && printf(STDERR "killing: %s\n", $G_testServerName);
        my($killCommand) = sprintf("docker kill %s", $G_testServerName);
        `$killCommand`;
    }
    if ($G_testNetworkCreated) {
        $debug && printf(STDERR "removing network: %s\n", $G_testServerName);
        my($rmNetCommand) = sprintf("docker network rm %s", $G_testNetwork);
        `$rmNetCommand`;
    }
    $debug && printf(STDERR "FINISHED CLEANUP...\n");
}

