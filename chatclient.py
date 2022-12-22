from socket import *
import sys
import pickle
import threading
# - addresses, port numbers etc. (a rudimentary way to replace a proper naming service)
import const


class RecvHandler(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self, daemon=True)
        self.client_socket = sock

    def run(self):
        while True:
            # print('Client receiving handler is ready.')
            # accepts connection from server
            (conn, addr) = self.client_socket.accept()
            # print('Server connected to me.')
            marshaled_msg_pack = conn.recv(1024)   # receive data from server
            # unmarshal message pack
            msg_pack = pickle.loads(marshaled_msg_pack)
            print("MESSAGE: " + msg_pack[0] + " - FROM: " + msg_pack[1])
            # simply send the server an Ack to confirm
            conn.send(pickle.dumps("ACK"))
            conn.close()

        # self.client_socket.close()


# User's name (as registered in the registry. E.g., Alice, Bob, ...)
me = str(sys.argv[1])
# socket for server to connect to this client
client_sock = socket(AF_INET, SOCK_STREAM)
# If using a proper naming service, client should know its
my_ip = const.registry[me][0]
# addresses (which it would register in the ns)
my_port = const.registry[me][1]
client_sock.bind((my_ip, my_port))
client_sock.listen(5)
#
# Put receiving thread to run
recv_handler = RecvHandler(client_sock)
recv_handler.start()
#
# Handle interactive loop
while True:
    server_sock = socket(AF_INET, SOCK_STREAM)  # socket to connect to server

    dest = input("ENTER DESTINATION: ")
    msg = input("ENTER MESSAGE: ")

    #
    # Connect to server
    try:
        server_sock.connect((const.CHAT_SERVER_HOST, const.CHAT_SERVER_PORT))
    except:
        print("Server is down. Exiting...")
        exit(1)
    #
    # Send message and wait for confirmation
    msg_pack = (msg, dest, me)
    marshaled_msg_pack = pickle.dumps(msg_pack)
    server_sock.send(marshaled_msg_pack)
    marshaled_reply = server_sock.recv(1024)
    reply = pickle.loads(marshaled_reply)
    if reply != "ACK":
        print("Error: Server did not accept the message (dest does not exist?)")
    else:
        # print("Received Ack from server")
        pass
    server_sock.close()
