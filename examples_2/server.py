import socket


class SP:
    @staticmethod
    def server():
        try:
            # Create a socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind to the socket
            s.bind(('127.0.0.1', 5999))

            # Listen at the socket
            # Now wait for client connection
            s.listen(1)
            while True:
                try:
                    # Accept connections
                    c, addr = s.accept()
                    print("Got connection from: ", addr)
                    while True:
                        # Receive data
                        data = c.recv(1024)
                        if data:
                            d = data.decode("utf-8")
                            print("Got data: " + str(d))
                            # Send data
                            c.send(str("ACK: " + str(d) + "...").encode("utf-8"))
                        else:
                            print("No more data from client: " + str(addr))
                            break
                finally:
                    c.close()
        except Exception as ex:
            print("Exception caught: " + str(ex))
            s.close()


SP.server()
