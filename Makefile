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

CLI_FILES := etc/repos/confluent.repo
SRV_FILES := etc/repos/confluent.repo etc/zookeeper/zoo.cfg etc/kafka/server.properties.auth etc/kafka/server.properties.no_auth scripts/runServer

.PHONY: test set-release-tags push clean client server all

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
	cd test && SCIMMA_TEST_TAG=$(TAG) pytest -v

set-release-tags:
	@$(eval RELEASE_TAG := $(shell echo $(GITHUB_REF) | awk -F- '{print $$2}'))
	@echo RELEASE_TAG =  $(RELEASE_TAG)
	@$(eval MAJOR_TAG   := $(shell echo $(RELEASE_TAG) | awk -F. '{print $$1}'))
	@echo MAJOR_TAG = $(MAJOR_TAG)
	@$(eval MINOR_TAG   := $(shell echo $(RELEASE_TAG) | awk -F. '{print $$2}'))
	@echo MINOR_TAG = $(MINOR_TAG)

push: set-release-tags
	@(echo $(RELEASE_TAG) | grep -P '^[0-9]+\.[0-9]+\.[0-9]+$$' > /dev/null ) || (echo Bad release tag: $(RELEASE_TAG) && exit 1)
	@eval "echo $$BUILDERCRED" | docker login --username $(BUILDER) --password-stdin
	docker tag $(CLI_IMG) $(CLI_NAME):$(RELEASE_TAG)
	docker tag $(SRV_IMG) $(SRV_NAME):$(RELEASE_TAG)
	docker tag $(CLI_IMG) $(CLI_NAME):$(MAJOR_TAG)
	docker tag $(SRV_IMG) $(SRV_NAME):$(MAJOR_TAG)
	docker tag $(CLI_IMG) $(CLI_NAME):$(MAJOR_TAG).$(MINOR_TAG)
	docker tag $(SRV_IMG) $(SRV_NAME):$(MAJOR_TAG).$(MINOR_TAG)
	docker push scimma/client:$(RELEASE_TAG)
	docker push scimma/server:$(RELEASE_TAG)
	docker push scimma/client:$(MAJOR_TAG)
	docker push scimma/server:$(MAJOR_TAG)
	docker push scimma/client:$(MAJOR_TAG).$(MINOR_TAG)
	docker push scimma/server:$(MAJOR_TAG).$(MINOR_TAG)
	docker push $(CLI_LTST)
	docker push $(SRV_LTST)
	rm -f $(HOME)/.docker/config.json

clean:
	rm -f *~
	rm -f downloads/*
	if [ -d downloads ]; then  rmdir downloads else /bin/true; fi
