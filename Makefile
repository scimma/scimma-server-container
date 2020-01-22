##
## Utilities
##
CURL := /usr/bin/curl

##
## ZOO
##
ZOO_VER   := 3.5.6
ZOO_TGZ   := apache-zookeeper-$(ZOO_VER).tar.gz
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
NAME   := scimma/server
TAG    := $(shell git log -1 --pretty=%H || echo MISSING )
IMG    := $(NAME):$(TAG)
LATEST := $(NAME):latest

DOWNLOADS := $(ZOO_TGZ) $(KAFKA_TGZ)
DOWNLOAD_DEPS := $(patsubst %,downloads/%,$(DOWNLOADS)) 

all:

print-%  : ; @echo $* = $($*)

downloads:

build: Dockerfile $(DOWNLOAD_DEPS)
	@if [ ! -z "$$(git status --porcelain)" ]; then echo "Directory is not clean. Commit your changes."; exit 1; fi
	docker build -t $(IMG) .

downloads/$(ZOO_TGZ): downloads
	$(CURL) -s -o downloads/$(ZOO_TGZ) $(ZOO_URL)

downloads/$(KAFKA_TGZ): downloads
	$(CURL) -s -o downloads/$(KAFKA_TGZ) $(KAFKA_URL)

clean:
	rm -f *~
	rm -f downloads/*
