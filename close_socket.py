def close_server_soket(server_socket, client_socket):
    try:
        client_socket.sendall(b"500")
    except Exception as e:
        print(f"Can't send internal error to client: {e}")
    except ConnectionAbortedError as cae:
        print(f"Error: Connection Aborted: {cae}")

    client_socket.close()
    server_socket.close()
    running = False

    return running
