import socket
import select
import msvcrt
import tkinter as tk
import protocol


def connect_to_server(ip, port):
    """
    Connects to the server at the given IP and port.
    :param ip: The server IP address.
    :type ip: str
    :param port: The server port.
    :type port: int
    :return: The connected socket.
    :rtype: socket
    """
    print("Connecting to server...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock


def clear_line():
    """
    Clears the current line in the console.
    """
    print('\r\033[K', end='', flush=True)


input_chars = []


def handle_input(sock):
    """
    Handles user input from the keyboard.
    :param sock: The connected socket.
    :type sock: socket
    :return: False if the client disconnected, else True.
    :rtype: bool
    """
    global input_chars

    if msvcrt.kbhit():  # Check if a key is pressed
        char = msvcrt.getch().decode()  # Get the pressed key
        if char == '\r':  # If Enter key is pressed, send the input

            data = ''.join(input_chars)
            input_chars.clear()
            if not data:
                msg = protocol.create_client_msg(protocol.EXIT)

            else:
                msg = protocol.create_client_msg(protocol.SEND_MSG, data)

            sock.send(msg.encode())

            if data == '':
                sock.close()
                return False

            clear_line()
            print("Write your message here: ", end='', flush=True)

        elif char == '\b':  # If Backspace is pressed, delete the last character
            if input_chars:
                input_chars.pop()
                print('\b \b', end='', flush=True)  # Erase the character from the console
        else:
            input_chars.append(char)
            print(char, end='', flush=True)  # Print the character to the console
    return True


def handle_output(sock):
    """
    Handles output from the server.
    :param sock: The connected socket.
    """
    rlist, _, _ = select.select([sock], [], [], 0)
    if sock in rlist:
        data_len = int(sock.recv(protocol.LENGTH_FIELD_SIZE).decode())
        data = sock.recv(data_len).decode()
        if data:
            clear_line()
            print(data)
            print("Write your message here: ", end='', flush=True)


def set_username(sock):
    while True:
        username = input("Enter your name: ")
        if not protocol.valid_username(username):
            print("This username is invalid.")
            continue

        msg = protocol.create_client_msg(protocol.SET_NAME, username)
        if not msg:
            print("Couldn't create message.")
            continue

        sock.send(msg.encode())
        length = int(sock.recv(protocol.LENGTH_FIELD_SIZE).decode())
        data = sock.recv(length).decode()
        if not data:
            print("Server error")
        elif data == "Ok":
            print("Username Accepted")
            break
        elif data == "Taken":
            print("This username is already taken.")


def chat_client(ip, port):
    """
    Main function to run the chat client.
    :param ip: The server IP address
    :type ip: str
    :param port: The server port.
    :type port: int
    """
    sock = connect_to_server(ip, port)
    set_username(sock)
    sock.setblocking(False)
    print("\n\nWrite your message here: ", end='', flush=True)
    while True:
        if not handle_input(sock):
            break
        handle_output(sock)
    print("\nConnection closed.")


if __name__ == "__main__":
    chat_client('127.0.0.1', 5555)
