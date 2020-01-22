FROM sl:latest
RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum -y install java-1.8.0-openjdk-headless.x86_64 java-1.8.0-openjdk-headless-debug.x86_64 emacs-nox perl 
ADD downloads/apache-zookeeper-*.tar.gz  /opt/zookeeper
