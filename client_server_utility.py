import des

def handle_to_client_connection(client_socket):
    """Send encrypted data to the client."""
    text = input("> Masukkan text: ")
    key = input("> Masukkan secret key (8 karakter): ")
    while len(key) != 8:
        print("> Panjang secret key tidak valid. Silakan masukkan 8 karakter.")
        key = input("> Masukkan secret key (8 karakter): ")

    print("\n--- Mode Enkripsi ---")
    print("> 1. Electronic Code Book (ECB)")
    print("> 2. Cipher Block Chaining (CBC)")
    encryption_mode = int(input(">> Pilih opsi enkripsi(1/2): "))

    if encryption_mode == 1:
        cipher_text = des.ecb_process(text, key, mode="encrypt")
        message = des.bin_to_hex(cipher_text)
        print(f">> ECB >> Teks Cipher (hex): {message}")
        client_socket.send(message.encode())
    elif encryption_mode == 2:
        iv = input(">> Masukkan initial vector (8 karakter): ")
        while len(iv) != 8:
            print(">> Panjang initial vector tidak valid. Silakan masukkan 8 karakter.")
            iv = input(">> Masukkan initial vector (8 karakter): ")

        cipher_text = des.cbc_process(text, key, iv, mode="encrypt")
        message = des.bin_to_hex(cipher_text)
        print(f">> CBC >> Teks Cipher (hex): {message}")
        client_socket.send(message.encode())
    else:
        print("> Opsi tidak valid, silakan coba lagi.")

def handle_from_server_connection(client_socket):
    """Receive encrypted data from the server."""
    message = client_socket.recv(1024)
    if not message:
        return
    text = message.decode()
    print(f"> Received from server: {text}")

    key = input("> Masukkan secret key (8 karakter): ")
    while len(key) != 8:
        print("> Panjang secretkey tidak valid. Silakan masukkan 8 karakter.")
        key = input("> Masukkan secret key (8 karakter): ")

    print("\n--- Mode Dekripsi ---")
    print("> 1. Electronic Code Book (ECB)")
    print("> 2. Cipher Block Chaining (CBC)")
    decryption_mode = int(input(">> Pilih opsi dekripsi(1/2): "))

    if decryption_mode == 1:
        decrypted_text = des.ecb_process(text, key, mode="decrypt")
        print(f">> ECB >> Teks Terdekripsi: {des.bin_to_text(decrypted_text)}")
    elif decryption_mode == 2:
        iv = input(">> Masukkan initial vector (8 karakter): ")
        while len(iv) != 8:
            print(">> Panjang initial vector tidak valid. Silakan masukkan 8 karakter.")
            iv = input(">> Masukkan initial vector (8 karakter): ")

        decrypted_text = des.cbc_process(text, key, iv, mode="decrypt")
        print(f">> CBC >> Teks Terdekripsi: {des.bin_to_text(decrypted_text)}")
    else:
        print("> Opsi tidak valid, silakan coba lagi.")