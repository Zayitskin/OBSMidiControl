import mido, socket

with mido.open_input("X-TOUCH COMPACT:X-TOUCH COMPACT MIDI 1 16:0") as port:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 50007))
        sock.listen(1)
        conn, addr = sock.accept()
        with conn:
            print("Connected by:",  addr)
            while True:
                for msg in port:
                    data = msg.dict()
                    print(data)
                    if data["type"] == "note_on":
                        packet = data["type"] + " " + str(data["note"])
                        conn.sendall(bytes(packet, "utf-8"))
