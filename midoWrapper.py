def closePort(signum, stackframe):
    port.close()

def pack(msg):
    if data["type"] == "note_on" or data["type"] == "note_off":
        return data["type"] + " " + data["note"]
    return data["type"] + " " + data["value"]

def midiControl(q, target = None):
    import mido
    import signal
    global port

    VALID_MESSAGE_TYPES = ["note_on", "note_off"]
    devices = mido.get_input_names()

    if target != None:
        for device in devices:
            if device.contains(sys.argv[1]):
                target = device
                break
    else:
        print("Choose a midi input device from the following:")
        for i in range(len(devices)):
            print(str(i + 1) + " " + devices[i])
        target = devices[int(input()) - 1]
            

    with mido.open_input(target) as port:
        signal.signal(signal.SIGTERM, closePort)
        while True:
            for msg in port:
                data = msg.dict()
                print(data)
                if data["type"] in VALID_MESSAGE_TYPES:
                    q.put(pack(data))
