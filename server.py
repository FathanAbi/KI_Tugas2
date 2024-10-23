import socket
import client_server_utility as csu

def start_server():
    """Start the server and listen for incoming connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 1234
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Listening on {host}:{port} ...")

    try:
        client_socket, addr = server_socket.accept()
        print(f"Got a connection from {addr}")

        while True:
            csu.handle_from_server_connection(client_socket)
            csu.handle_to_client_connection(client_socket)

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server()
