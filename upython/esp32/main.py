def read_credentials():
    with open("credentials") as f:
        essid = f.readline().strip()
        password = f.readline().strip()
    return (essid, password)

def do_connect(essid, password):
    import network
    global STA_IF
    STA_IF = network.WLAN(network.STA_IF)
    if not STA_IF.isconnected():
        print("connecting to network {}...".format(essid))
        STA_IF.active(True)
        STA_IF.connect(essid, password)
        while not STA_IF.isconnected():
            pass
    print('network config:', STA_IF.ifconfig())

credentials = read_credentials()
do_connect(credentials[0], credentials[1])
del credentials
del read_credentials
