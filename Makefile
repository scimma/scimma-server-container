##
## Utilities
##
CURL := /usr/bin/curl

##
## ZOO
##
ZOO_VER   := 3.5.6
ZOO_TGZ   := apache-zookeeper-$(ZOO_VER)-bin.tar.gz
ZOO_URL   := http://apache.cs.utah.edu/zookeeper/zookeeper-$(ZOO_VER)/$(ZOO_TGZ)

##
## Kafka
##
KAFKA_VER := 2.4.0
SCALA_VER := 2.12
KAFKA_TGZ := kafka_$(SCALA_VER)-$(KAFKA_VER).tgz
KAFKA_URL := http://apache.cs.utah.edu/kafka/$(KAFKA_VER)/$(KAFKA_TGZ)

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

DOWNLOADS := $(ZOO_TGZ) $(KAFKA_TGZ)

all: client server

print-%  : ; @echo $* = $($*)

downloads:
	mkdir -p downloads

client: Dockerfile.client downloads/$(KAFKA_TGZ)
	@if [ ! -z "$$(git status --porcelain)" ]; then echo "Directory is not clean. Commit your changes."; exit 1; fi
	docker build -f $< -t $(CLI_IMG)

server: Dockerfile.server downloads/$(ZOO_TGZ) downloads/$(KAFKA_TGZ)
	@if [ ! -z "$$(git status --porcelain)" ]; then echo "Directory is not clean. Commit your changes."; exit 1; fi
	docker build -f $< -t $(SRV_IMG) .

downloads/$(ZOO_TGZ): downloads
	$(CURL) -s -o downloads/$(ZOO_TGZ) $(ZOO_URL)

downloads/$(KAFKA_TGZ): downloads
	$(CURL) -s -o downloads/$(KAFKA_TGZ) $(KAFKA_URL)

clean:
	rm -f *~
	rm -f downloads/*
