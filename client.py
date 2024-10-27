import socket
import client_server_utility as csu

def client_program():
    """Connect to the server and start exchanging messages."""
    host = '127.0.0.1'
    port = 1234
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    try:
        while True:
            csu.handle_to_another_connection(client_socket)
            csu.handle_from_other_connection(client_socket)

    except KeyboardInterrupt:
        print("Client disconnecting.")
    finally:
        client_socket.close()

if __name__ == '__main__':
    client_program()
