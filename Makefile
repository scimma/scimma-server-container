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

.PHONY: test set-release-tag push clean client server all

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

set-release-tag:
	$(eval RELEASE_TAG=`echo $(GITHUB_REF) | awk -F/ '{print $$$$3}'`)

push: set-release-tag
	@eval "echo $$BUILDERCRED" | docker login --username $(BUILDER) --password-stdin
	docker tag $(CLI_IMG) $(CLI_NAME):$(RELEASE_TAG)
	docker tag $(SRV_IMG) $(SRV_NAME):$(RELEASE_TAG)
	docker push scimma/client:$(RELEASE_TAG)
	docker push scimma/server:$(RELEASE_TAG)

clean:
	rm -f *~
	rm -f downloads/*
	if [ -d downloads ]; then  rmdir downloads else /bin/true; fi
