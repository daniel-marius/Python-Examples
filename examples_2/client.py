import socket


class SP:
    @staticmethod
    def client():
        try:
            # Create a socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the socket
            s.connect(('127.0.0.1', 5999))
            while True:
                data = input("Enter data to be sent to server: \n")
                if not data:
                    break
                else:
                    # Receive and send data
                    s.send(data.encode("utf-8"))
                    reply = s.recv(1024).decode("utf-8")
                    print(str(reply))
            s.close()
        except Exception as ex:
            print("Exception caught: " + str(ex))


SP.client()
