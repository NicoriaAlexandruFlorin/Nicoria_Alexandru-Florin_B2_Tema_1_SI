import socket
import Cryptodome.Cipher.AES
import binascii
from Cryptodome.Util.Padding import pad, unpad
import time

K3 = "A%D*G-KaPdSgVkYp"  # cheie utilizata in criptarea cheilor
K1 = ""  # CBC
K2 = ""  # OFB
K = ""
IV = "7x!z%C*F-JaNdRgU"
comm_mode = ""
q = 50
index = 0


def init():
    global q
    return q


def nodeA_thread():
    global comm_mode
    host_address = socket.gethostname()
    port = 5000

    nodeA = socket.socket()
    nodeA.bind((host_address, port))
    nodeA.listen(2)
    connection, address = nodeA.accept()
    message_nodeB = ""
    while message_nodeB != "Mod setat":
        message_nodeB = connection.recv(1024).decode()
        if message_nodeB != "Mod setat":
            message_nodeA = input(message_nodeB)
        else:
            comm_mode = message_nodeA
            message_nodeA = "Disconnected"
            print(message_nodeB)
            print("S-a oprit conexiunea , se va reface cand se trimit cheile")
            print("Metoda de comunicare este: " + comm_mode)
        connection.send(message_nodeA.encode())

    connection.close()


def nodeA_client_thread():
    global comm_mode
    global K
    port1 = 5001
    host_address = socket.gethostname()

    nodeA = socket.socket()
    time.sleep(2)
    nodeA.connect((host_address, port1))

    message_nodeKM = ""
    message_nodeA = ""
    message_nodeKM = nodeA.recv(45).decode()
    print(message_nodeKM)
    print("Modul de comunicare este: " + comm_mode)
    message_nodeA = comm_mode
    nodeA.send(message_nodeA.encode())

    message_nodeKM = nodeA.recv(16).decode('ISO-8859-1')
    if (comm_mode == "OFB"):
        K2 = message_nodeKM
        print("Pentru " + comm_mode + " a fost criptata cheia " + K2)
        K_sent = K2
    else:
        K1 = message_nodeKM
        print("Pentru " + comm_mode + " a fost criptata cheia " + K1)
        K_sent = K1

    nodeA.close()
    port = 5002
    nodeA = socket.socket()
    nodeA.connect((host_address, port))
    print("Se trimite cheia catre B")
    nodeA.send(K_sent.encode('ISO-8859-1'))
    nodeA.close()
    print("Decriptam cheia")
    aes = Cryptodome.Cipher.AES.new(K3.encode('ISO-8859-1'), Cryptodome.Cipher.AES.MODE_ECB)
    K = aes.decrypt(K_sent.encode('ISO-8859-1'))
    print("Cheia decriptata este " + K.hex() + " str: " + str(
        K.decode('ISO-8859-1')) + " in modul de comunicare " + comm_mode)


def xor_string(s1, s2):
    return "".join([chr(ord(a) ^ ord(b)) for a, b in zip(s1, s2)])


def transport():
    line = open("H:\pythonProject\input.txt")
    content = line.read()
    if(len(content)%16!=0):
        for i in range(len(content)%16):
            content=content+" "


    global comm_mode
    global K
    global IV
    global index
    global q
    host_address = socket.gethostname()
    port = 5003
    nodeA = socket.socket()
    nodeA.connect((host_address, port))

    aes = Cryptodome.Cipher.AES.new(K, Cryptodome.Cipher.AES.MODE_ECB)
    if comm_mode == "CBC":
        for i in range(index, len(content), 16):
            block = content[i:i + 16]
            if len(block) != 16:
                for j in range(16 - len(block)):
                    block = block + " "
            xored = xor_string(block, IV)
            xored_enc = aes.encrypt(xored.encode('ISO-8859-1'))
            IV = xored_enc.decode('ISO-8859-1')

            nodeA.send(IV.encode('ISO-8859-1'))
            q = q - 1
            if q == 0:
                index = i+16
                q = 50
                string_gol=""
                nodeA.send(string_gol.encode('ISO-8859-1'))
                nodeA.close()
                return None
            elif i==len(content)-1:
                string_gol = ""
                nodeA.send(string_gol.encode('ISO-8859-1'))
                index = i+16
                nodeA.close()
                return None



    elif comm_mode == "OFB":
        for i in range(index, len(content), 16):
            block = content[i:i + 16]
            if len(block) != 16:
                for j in range(16 - len(block)):
                    block = block + " "
            IV_encrypted = aes.encrypt(IV.encode('ISO-8859-1'))
            xored = xor_string(block, IV_encrypted.decode('ISO-8859-1'))
            IV = IV_encrypted.decode('ISO-8859-1')
            nodeA.send((xored.encode('ISO-8859-1')))
            q = q - 1
            if q == 0:
                string_gol = ""
                nodeA.send(string_gol.encode('ISO-8859-1'))
                nodeA.close()
                index = i+16
                q = 50
                return None
            elif i == len(content) - 1:
                string_gol = ""
                nodeA.send(string_gol.encode('ISO-8859-1'))
                index = i+16
                nodeA.close()
                return None


    nodeA.close()


if __name__ == '__main__':
    line = open("H:\pythonProject\input.txt")
    content = line.read()
    nr =len(content)
    line.close()

    while index<nr:
         nodeA_thread()
         nodeA_client_thread()
         transport()


