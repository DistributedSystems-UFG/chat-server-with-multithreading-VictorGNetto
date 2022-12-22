from socket import *
import pickle
import threading
import sys
# - addresses, port numbers etc. (a rudimentary way to replace a proper naming service)
import const


class WorkerThread(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self, daemon=True)
        self.conn = conn
        print("Starting a new Worker Thread")

    def run(self):
        marshaled_msg_pack = self.conn.recv(1024)  # receive data from client
        msg_pack = pickle.loads(marshaled_msg_pack)
        msg = msg_pack[0]
        dest = msg_pack[1]
        src = msg_pack[2]
        # log the message, source and destination
        print("RELAYING MSG: " + msg + " - FROM: " + src + " - TO: " + dest)

        # check that the destination exists
        try:
            dest_addr = const.registry[dest]
        except:
            self.conn.send(pickle.dumps("NACK"))
            self.conn.close()
            return
        else:
            self.conn.send(pickle.dumps("ACK"))
            self.conn.close()

        # forward the message to the destination
        # socket to connect to clients
        client_sock = socket(AF_INET, SOCK_STREAM)
        dest_ip = dest_addr[0]
        dest_port = dest_addr[1]
        try:
            client_sock.connect((dest_ip, dest_port))
        except:
            print("Error: Destination client is down")
            return
        msg_pack = (msg, src)
        marshaled_msg_pack = pickle.dumps(msg_pack)
        client_sock.send(marshaled_msg_pack)
        marshaled_reply = client_sock.recv(1024)
        reply = pickle.loads(marshaled_reply)
        if reply != "ACK":
            print("Error: Destination client did not receive message properly")
        else:
            # print("Server: Received Ack from client")
            pass
        client_sock.close()


class DispatcherThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        print("Chat Server is ready...")

    def run(self):
        # socket for clients to connect to this server
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.bind((const.CHAT_SERVER_HOST, const.CHAT_SERVER_PORT))
        server_sock.listen(5)  # may change if too many clients

        while True:
            (conn, addr) = server_sock.accept()

            # create a worker to handle the connection
            worker = WorkerThread(conn)
            worker.start()


# create and start the Dispatcher Thread
dispacther = DispatcherThread()
dispacther.start()

# Make the python's main thread to be accessible from keyboard.
# This can be useful if we want to stop the process
while True:
    cmd = input()

    # stop the server gracefully
    if cmd.upper() == 'CLOSE':
        print('Chat server stoping...')
        sys.exit(0)
