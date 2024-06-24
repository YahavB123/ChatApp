import socket
import select
import protocol
from datetime import datetime

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = "0.0.0.0"

addr_to_name = {}


def print_client_sockets(client_sockets):
    """
    Prints the list of currently connected client sockets.
    :param client_sockets: List of the connected client sockets.
    :type client_sockets: list<socket>
    """
    if len(client_sockets) == 0:
        print('\t', 'None')
    else:
        for c in client_sockets:
            print("\t", c.getpeername())


def setup_server(ip, port):
    """
    Sets up the server socket.
    :param ip: The IP address to bind the server to.
    :type: str
    :param port: The port to bind the server to.
    :type port: int
    :return: The configured server socket.
    :rtype: socket
    """
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(False)
    server_socket.bind((ip, port))
    server_socket.listen()
    print("Listening for clients...")
    return server_socket


def handle_new_connection(server_socket, client_sockets):
    """
    Handles new client connections.
    :param server_socket: The server socket.
    :type server_socket: socket
    :param client_sockets: List of the connected client sockets.
    :type client_sockets: list<socket>
    """
    connection, client_address = server_socket.accept()
    print("New client joined!", client_address)
    client_sockets.append(connection)
    print("Current clients:")
    print_client_sockets(client_sockets)


def handle_client_message(current_socket, client_sockets, messages_to_send):
    """
    Handles incoming messages from clients.
    :param current_socket: The client socket that sent the message.
    :type current_socket: socket
    :param client_sockets: List of the connected client sockets.
    :type client_sockets: list<socket>
    :param messages_to_send: List of the messages waiting to be sent to other clients.
    :type messages_to_send: list<str>
    """
    """

    """
    cmd = int(current_socket.recv(protocol.CMD_FIELD_SIZE).decode())
    if cmd == 2:
        print("Connection closed by: ", addr_to_name[current_socket.getpeername()])
        client_sockets.remove(current_socket)

        time = datetime.now().strftime("%H:%M")
        username = addr_to_name[current_socket.getpeername()]
        reply = f'{time} {username} has left the chat.'
        msg = protocol.create_server_msg(reply)
        messages_to_send.append((client_sockets.copy(), msg))

        current_socket.close()

        print("Current clients:")
        print_client_sockets(client_sockets)
        return

    params = []
    for i in range(protocol.PARAM_NUM[cmd]):
        p_len = int(current_socket.recv(protocol.LENGTH_FIELD_SIZE).decode())
        p = current_socket.recv(p_len).decode()
        params.append(p)

    if cmd == 0:
        if params[0] not in addr_to_name.values():
            addr_to_name[current_socket.getpeername()] = params[0]
            reply = "Ok"
        else:
            reply = "Taken"
        msg = protocol.create_server_msg(reply).encode()
        current_socket.send(msg)

    elif cmd == 1:
        time = datetime.now().strftime("%H:%M")
        username = addr_to_name[current_socket.getpeername()]
        reply = f'{username}: {params[0]}'
        msg = protocol.create_server_msg(f'{time} {reply}')
        messages_to_send.append((client_sockets.copy(), msg))


def send_messages(messages_to_send, wlist):
    """
    Broadcasts messages to all connected clients except the sender.
    :param messages_to_send: List of the messages waiting to sent to other clients.
    :type messages_to_send: list<(list<socket>, str)>
    :param wlist: List of the socket ready for writing.
    :type wlist: list<socket>
    """
    for message in messages_to_send:
        receivers, data = message
        for receiver in receivers:
            if receiver in wlist:
                receiver.send(data.encode())
                receivers.remove(receiver)
        if len(receivers) == 0:
            messages_to_send.remove(message)


def run_server():
    """
    Main function to run the server.
    """
    server_socket = setup_server(SERVER_IP, SERVER_PORT)
    client_sockets = []
    messages_to_send = []

    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])

        for current_socket in rlist:
            # new connection is made
            if current_socket is server_socket:
                handle_new_connection(server_socket, client_sockets)
            # existing client sent data
            else:
                handle_client_message(current_socket, client_sockets, messages_to_send)

        send_messages(messages_to_send, wlist)


if __name__ == "__main__":
    run_server()
