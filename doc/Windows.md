## Windows Specific Notes

Tested on a Windows 10 Pro machine with [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10) installed.

In essence, a fairly vanilla installation of WSL and Docker Desktop (Community Edition of Docker is fine), as described [in this article](https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly) will suffice (although it may require the odd reboot).

In essence, the Docker server runs on the Windows side under Hyper-V and the Docker client is on the Linux side and connects to the Docker server side via setting the `$DOCKER_HOST` environment variable. As soon as you can connect to the Docker server, for example with `docker ps`, you can run all the instructions above in WSL.

**Note 1** Using [ConEmu](https://conemu.github.io/) or another tabbed console makes the "Extra Credit" section rather more convenient (and is recommended in any case, to get away from the limited console which ships with Windows).

**Note 2** WSL 2, currently available in Insider Windows builds, should allow Docker to be run entirely on the WSL/Linux side. For details on installation, see [this article](https://docs.microsoft.com/en-us/windows/wsl/wsl2-install)


