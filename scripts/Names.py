def getHostnames ():
    cmd = "ip -4 -o address"
    lines = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE).stdout.read().decode().splitlines()
    names = []
    for line in lines:
        ipm = re.match(r'\S+\s+\S+\s+inet\s+([0-9\.]+)\/', line)
        if ipm != None:
            names.extend(namesForAddress(ipm.group(1)))
    retNames = []
    for name in list(set(names)):
        um = re.match(r'^([a-zA-Z0-9\-\.]+)$')
        if um != None:
        retNames.append(name)
    return retNames

def namesForAddress (addr):
    name = socket.getfqdn(addr)
    names = [name]
    nm = re.match(r'^([^\.]+)\.(.+)$', name)
    if nm != None:
        names.append(nm.group(1))
    return names
