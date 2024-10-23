import socket
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

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

# tabel permuatasi awal 
initial_perm = [58, 50, 42, 34, 26, 18, 10, 2,
                60, 52, 44, 36, 28, 20, 12, 4,
                62, 54, 46, 38, 30, 22, 14, 6,
                64, 56, 48, 40, 32, 24, 16, 8,
                57, 49, 41, 33, 25, 17, 9, 1,
                59, 51, 43, 35, 27, 19, 11, 3,
                61, 53, 45, 37, 29, 21, 13, 5,
                63, 55, 47, 39, 31, 23, 15, 7]

# Tabel ekspandi d-box
exp_d = [32, 1, 2, 3, 4, 5, 4, 5,
         6, 7, 8, 9, 8, 9, 10, 11,
         12, 13, 12, 13, 14, 15, 16, 17,
         16, 17, 18, 19, 20, 21, 20, 21,
         22, 23, 24, 25, 24, 25, 26, 27,
         28, 29, 28, 29, 30, 31, 32, 1]
 
# table permutasi untuk straight d box
per = [16,  7, 20, 21,
       29, 12, 28, 17,
       1, 15, 23, 26,
       5, 18, 31, 10,
       2,  8, 24, 14,
       32, 27,  3,  9,
       19, 13, 30,  6,
       22, 11,  4, 25]
 
# tabel s box
sbox = [[[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
         [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
         [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
         [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
 
        [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
         [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
         [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
         [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
 
        [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
         [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
         [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
         [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
 
        [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
         [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
         [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
         [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
 
        [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
         [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
         [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
         [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
 
        [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
         [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
         [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
         [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
 
        [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
         [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
         [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
         [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
 
        [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
         [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
         [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
         [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]]
 
# table permutasi akhir
final_perm = [40, 8, 48, 16, 56, 24, 64, 32,
              39, 7, 47, 15, 55, 23, 63, 31,
              38, 6, 46, 14, 54, 22, 62, 30,
              37, 5, 45, 13, 53, 21, 61, 29,
              36, 4, 44, 12, 52, 20, 60, 28,
              35, 3, 43, 11, 51, 19, 59, 27,
              34, 2, 42, 10, 50, 18, 58, 26,
              33, 1, 41, 9, 49, 17, 57, 25]

# parse binary menjadi 64 bit block sebelum di encrypt
def parse(binary):
  chunks = []
  for i in range(0, len(binary), 64):
    chunk = binary[i:i+64]
    
    chunks.append(chunk)
  return chunks

# binary to decimal
def binaryToDecimal(binary):
  decimal, i = 0, 0
  while(binary != 0):
    dec = binary % 10
    decimal = decimal + dec * pow(2, i)
    binary = binary//10
    i += 1
  return decimal

# decimal to binary 
def decimalToBinary(num):
  res = bin(num).replace("0b", "")
  if(len(res) % 4 != 0):
    div = len(res) / 4
    div = int(div)
    counter = (4 * (div + 1)) - len(res)
    for i in range(0, counter):
      res = '0' + res

  return res

def xor(a, b):
  ans = ""
  for i in range(len(a)):
    if a[i] == b[i]:
      ans = ans + "0"
    else:
      ans = ans + "1"
  return ans

 
def hexToBinary(s):
  n = int(s, 16) 
  bStr = '' 
  while n > 0: 
    bStr = str(n % 2) + bStr 
    n = n >> 1   
  return str(bStr)

def binaryToHex(s):
  num = int(s, 2)
  
  # convert int to hexadecimal
  hex_num = hex(num)
  return(hex_num)

def plaintextToBinary(plaintext):
  binary_string = ""
  for char in plaintext:
    binary_char = bin(ord(char))[2:].zfill(8)  # Convert to binary and remove '0b' prefix, pad with zeros
    binary_string += binary_char   # Append binary char with a space separator

  return binary_string.rstrip()

def permute(k, arr, n):
  permutation = ""
  for i in range(0, n):
    permutation = permutation + k[arr[i] - 1]
  return permutation

 
def shift_left(k, nth_shifts):
  s = ""
  for i in range(nth_shifts):
    for j in range(1, len(k)):
      s = s + k[j]
    s = s + k[0]
    k = s
    s = ""
  return k

# key generation untuk tiap round des
def generateKey(bin_key):
  keyp = [57, 49, 41, 33, 25, 17, 9,
      1, 58, 50, 42, 34, 26, 18,
      10, 2, 59, 51, 43, 35, 27,
      19, 11, 3, 60, 52, 44, 36,
      63, 55, 47, 39, 31, 23, 15,
      7, 62, 54, 46, 38, 30, 22,
      14, 6, 61, 53, 45, 37, 29,
      21, 13, 5, 28, 20, 12, 4]
 
  # getting 56 bit key from 64 bit using the parity bits
  key = permute(bin_key, keyp, 56)

  shift_table = [1, 1, 2, 2,
               2, 2, 2, 2,
               1, 2, 2, 2,
               2, 2, 2, 1]
 
  # Key- Compression Table : Compression of key from 56 bits to 48 bits
  key_comp = [14, 17, 11, 24, 1, 5,
              3, 28, 15, 6, 21, 10,
              23, 19, 12, 4, 26, 8,
              16, 7, 27, 20, 13, 2,
              41, 52, 31, 37, 47, 55,
              30, 40, 51, 45, 33, 48,
              44, 49, 39, 56, 34, 53,
              46, 42, 50, 36, 29, 32]
  
  # Splitting
  left = key[0:28]    # rkb for RoundKeys in binary
  right = key[28:56]  # rk for RoundKeys in hexadecimal
  
  rkb = []
  

  for i in range(0, 16):
    # Shifting the bits by nth shifts by checking from shift table
    left = shift_left(left, shift_table[i])
    right = shift_left(right, shift_table[i])

    # Combination of left and right string
    combine_str = left + right

    # Compression of key from 56 to 48 bits
    round_key = permute(combine_str, key_comp, 48)

    rkb.append(round_key)

  return rkb

def des(binary, rkb):
  binary = permute(binary, initial_perm, 64)

  # print("After initial permutation", binaryToHex(binary))
  
  left = binary[0:32]
  right = binary[32:64]

  for i in range(0, 16):
    right_expanded = permute(right, exp_d, 48)

    xor_x = xor(right_expanded, rkb[i])

    sbox_str = ""
    for j in range(0, 8):
      row = binaryToDecimal(int(xor_x[j * 6] + xor_x[j * 6 + 5]))
      col = binaryToDecimal(
          int(xor_x[j * 6 + 1] + xor_x[j * 6 + 2] + xor_x[j * 6 + 3] + xor_x[j * 6 + 4]))
      val = sbox[j][row][col]
      sbox_str = sbox_str + decimalToBinary(val)

    sbox_str = permute(sbox_str, per, 32)
    result = xor(left, sbox_str)
    left = result

    if(i != 15):
      left, right = right, left
  
  combine = left + right
  cipher_text = permute(combine, final_perm, 64)
  return cipher_text
 

def encrypt(binary, rkb):
  chunks = parse(binary)  

  encrypted = ""

  for chunk in chunks:
    encrypted_chunk = des(chunk, rkb)
    encrypted = encrypted + encrypted_chunk

  return encrypted



def binaryToPlaintext(binary_data, encoding="utf-8"):
  # Convert binary data to bytes
  bytes_data = bytes(int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8))

  # Decode bytes using the specified encoding
  plaintext = bytes_data.decode(encoding)

  return plaintext


# Client functionality
def client_program(binary):
    host = '127.0.0.1'
    port = 1234

    # create socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server
    client_socket.connect((host, port))

    # send message
    client_socket.send(binary.encode())

    # close socket
    client_socket.close()

# Unit test for the client code
class TestClient(unittest.TestCase):
    @patch('socket.socket')  # Mock the socket object
    def test_client_program(self, mock_socket):
        # Create a mock socket instance
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Call the function under test
        client_program()

        # Assert that connect was called with the right address
        mock_socket_instance.connect.assert_called_once_with(('127.0.0.1', 12345))
        print(f"connect called with: {mock_socket_instance.connect.call_args}")

        # Assert that send was called with the right message
        mock_socket_instance.send.assert_called_once_with(b'Hello, Server!')
        print(f"send called with: {mock_socket_instance.send.call_args}")

        # Assert that close was called
        mock_socket_instance.close.assert_called_once()
        print(f"close called with: {mock_socket_instance.close.call_args}")


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

if __name__ == '__main__':
    plaintext = input("masukkan text yang ingin diencrypt: ")
    key = input("masukkan key: ")

    plaintext = pad(plaintext, 8)

    rkb = generateKey(plaintextToBinary(key))

    plaintext_binary = plaintextToBinary(plaintext)

    encrypted = encrypt(plaintext_binary, rkb)

    
    print("encrypted hex: ", binaryToHex(encrypted).split('0x')[1])
    
    
    rkb_rev = rkb[::-1]
    

    decrypted = encrypt(encrypted, rkb_rev)
    print("decrypted: ", unpad(binaryToPlaintext(decrypted), 8))
    # Run unittest with a custom runner that suppresses output
    # Make sure to uncomment this before uploading the code to domjudge
    client_program(encrypted)

    # Uncomment this if you want to run the client program, not running the unit test
    # client_program()
