## Mac/MacPorts Notes 

Under macOS Catalina (10.15.1) the build and demo were run using:

    1. The built-in make, curl, and git
    2. Docker from mac ports (https://www.macports.org/)
    3. Docker Compose downloaded via:

``` sh
           curl -L https://github.com/docker/compose/releases/download/1.25.3/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
           chmod +x /usr/local/bin/docker-compose
```

The docker-compose provided by mac ports did not work when tested.

In order to run Docker commands, that is, to have a working docker installation
when using docker from Mac Ports and VirtualBox, you will need to manually setup
your docker server.

Do this once:

```sh
    docker-machine create --driver virtualbox scimma
```

Do this after the last command and after every reboot:

```sh
    docker-machine start scimma
```

Do this, as root, every time that you run a new shell (open a new window) in which you want to run docker commands associated with the scimma containers:

```
        eval $(docker-machine env scimma)
```

You can run ``docker-machine env dev`` on the command line to see what would be evaluated.

Note: this is for people who like the command line and want to use very basic tools. For a more user-friendly experience, try [Docker Desktop](https://docs.docker.com/docker-for-mac/install/).
