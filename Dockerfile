FROM sl:latest
RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm net-tools \
                   java-1.8.0-openjdk-headless.x86_64 java-1.8.0-openjdk-headless-debug.x86_64 emacs-nox perl 
ADD downloads/apache-zookeeper-*.tar.gz  /opt
ADD downloads/kafka_*.tgz /opt
RUN ln -s /opt/apache-zookeeper-* /opt/apache-zookeeper && mkdir /tmp/zookeeper
RUN ln -s /opt/kafka_* /opt/kafka 
COPY etc/zookeeper/zoo.cfg /opt/apache-zookeeper/conf/zoo.cfg
COPY etc/kafka/server.properties /opt/kafka/config/server.properties
COPY scripts/runServer /root/runServer
RUN  chmod ugo+rx /root/runServer
WORKDIR /tmp
EXPOSE 9090/tcp
ENTRYPOINT ["/root/runServer"]
