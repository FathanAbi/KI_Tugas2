import des

# padding dan unpadding mengguankan PKCS7
def pad(string, block_size):
  padding_number = block_size - len(string) % block_size
  if padding_number == block_size:
    return string
  padding = chr(padding_number) * padding_number
  return string + padding

def unpad(string, block_size):
  if not string: return string
  if len(string) % block_size:
    raise TypeError('string is not a multiple of the block size.')
  padding_number = ord(string[-1])
  if padding_number >= block_size:
    return string
  else:
    if all( padding_number == ord(c) for c in string[-padding_number:] ):
      return string[0:-padding_number]
    else:
      return string


def handle_to_another_connection(client_socket):
    """Send encrypted data to the other device."""
    text = input("> Masukkan text: ")
    text = pad(text, 8)
    key = input("> Masukkan secret key (8 karakter): ")
    while len(key) != 8:
        print("> Panjang secret key tidak valid. Silakan masukkan 8 karakter.")
        key = input("> Masukkan secret key (8 karakter): ")

    print("\n--- Mode Enkripsi ---")
    print("> 1. Electronic Code Book (ECB)")
    print("> 2. Cipher Block Chaining (CBC)")
    print("> 3. Cipher FeedBack (CFB)")
    encryption_mode = int(input(">> Pilih opsi enkripsi(1/2/3): "))

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
    elif encryption_mode == 3:
        iv = input(">> Masukkan initial vector (8 karakter): ")
        while len(iv) != 8:
            print(">> Panjang initial vector tidak valid. Silakan masukkan 8 karakter.")
            iv = input(">> Masukkan initial vector (8 karakter): ")

        cipher_text = des.cfb_process(text, key, iv, mode="encrypt")
        message = des.bin_to_hex(cipher_text)
        print(f">> CFB >> Teks Cipher (hex): {message}")
        client_socket.send(message.encode())
    else:
        print("> Opsi tidak valid, silakan coba lagi.")

def handle_from_other_connection(client_socket):
    """Receive encrypted data from the other device."""
    message = client_socket.recv(1024)
    if not message:
        return
    text = message.decode()
    print(f"> Received from other device: {text}")

    key = input("> Masukkan secret key (8 karakter): ")
    while len(key) != 8:
        print("> Panjang secretkey tidak valid. Silakan masukkan 8 karakter.")
        key = input("> Masukkan secret key (8 karakter): ")

    print("\n--- Mode Dekripsi ---")
    print("> 1. Electronic Code Book (ECB)")
    print("> 2. Cipher Block Chaining (CBC)")
    print("> 3. Cipher FeedBack (CFB)")
    decryption_mode = int(input(">> Pilih opsi dekripsi(1/2/3): "))

    if decryption_mode == 1:
        decrypted_text = des.ecb_process(text, key, mode="decrypt")
        print(f">> ECB >> Teks Terdekripsi: {unpad(des.bin_to_text(decrypted_text), 8)}")
    elif decryption_mode == 2:
        iv = input(">> Masukkan initial vector (8 karakter): ")
        while len(iv) != 8:
            print(">> Panjang initial vector tidak valid. Silakan masukkan 8 karakter.")
            iv = input(">> Masukkan initial vector (8 karakter): ")

        decrypted_text = des.cbc_process(text, key, iv, mode="decrypt")
        print(f">> CBC >> Teks Terdekripsi: {unpad(des.bin_to_text(decrypted_text), 8)}")
    elif decryption_mode == 3:
        iv = input(">> Masukkan initial vector (8 karakter): ")
        while len(iv) != 8:
            print(">> Panjang initial vector tidak valid. Silakan masukkan 8 karakter.")
            iv = input(">> Masukkan initial vector (8 karakter): ")

        decrypted_text = des.cfb_process(text, key, iv, mode="decrypt")
        print(f">> CFB >> Teks Terdekripsi: {unpad(des.bin_to_text(decrypted_text), 8)}")
    else:
        print("> Opsi tidak valid, silakan coba lagi.")