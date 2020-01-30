##
## For tagging the container:
##
SRV_NAME := scimma/server
CLI_NAME := scimma/client

TAG      := $(shell git log -1 --pretty=%H || echo MISSING )
SRV_IMG  := $(SRV_NAME):$(TAG)
CLI_IMG  := $(CLI_NAME):$(TAG)
SRV_LTST := $(SRV_NAME):latest
CLI_LTST := $(CLI_NAME):latest

CLI_FILES := etc/repos/confluent.repo scripts/runClient 
SRV_FILES := etc/repos/confluent.repo etc/zookeeper/zoo.cfg etc/kafka/server.properties scripts/runServer

.PHONY: test

all: client server

print-%  : ; @echo $* = $($*)

client: Dockerfile.client $(CLI_FILES)
	@if [ ! -z "$$(git status --porcelain)" ]; then echo "Directory is not clean. Commit your changes."; exit 1; fi
	docker build -f $< -t $(CLI_IMG) .
	docker tag $(CLI_IMG) $(CLI_LTST)

server: Dockerfile.server $(SRV_FILES)
	@if [ ! -z "$$(git status --porcelain)" ]; then echo "Directory is not clean. Commit your changes."; exit 1; fi
	docker build -f $< -t $(SRV_IMG) .
	docker tag $(SRV_IMG) $(SRV_LTST)

test:
	cd test && ./test.pl $(TAG)

clean:
	rm -f *~
	rm -f downloads/*
	rmdir downloads
