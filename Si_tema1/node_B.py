import socket
import Cryptodome.Cipher.AES

K3 = "A%D*G-KaPdSgVkYp"  # cheie utilizata in criptarea cheilor
comm_mode = ""
K = ""
KEY = ""
IV = "7x!z%C*F-JaNdRgU"
q=50
output = ""
def nodeB_client_thread():
    global comm_mode
    host_address = socket.gethostname()
    port = 5000
    nodeB = socket.socket()
    nodeB.connect((host_address, port))

    message_nodeB = "Mod de comunicare:\n"
    message_nodeA = ""

    while message_nodeA != 'Disconnected':
        nodeB.send(message_nodeB.encode())
        message_nodeA = nodeB.recv(1024).decode()

        if message_nodeA != "Disconnected":
            if message_nodeA != "OFB" and message_nodeA != "CBC":
                message_nodeB = "Mod invalid :"
                print("Modul de comunicare transmis de A este invalid:")
            else:
                print("Modul de comunicare este" + str(message_nodeA))
                message_nodeB = "Mod setat"
                comm_mode = message_nodeA
        else:
            print("S-a oprit conexiunea , se va reface cand se trimit cheile")
            print("Metoda de comunicare este:" + comm_mode)
    nodeB.close()


def nodeB_server_thread():
    global comm_mode
    global K
    host_address = socket.gethostname()
    port = 5002

    nodeB = socket.socket()
    nodeB.bind((host_address, port))
    nodeB.listen(2)
    connection, address = nodeB.accept()
    K = connection.recv(16).decode('ISO-8859-1')
    print("Cheia primita este " + K)

    connection.close()
    print("Se decripteaza cheia...")
    aes = Cryptodome.Cipher.AES.new(K3.encode('ISO-8859-1'), Cryptodome.Cipher.AES.MODE_ECB)
    K = aes.decrypt(K.encode('ISO-8859-1'))
    print("Cheia decriptata este " + str(K.decode('ISO-8859-1')) + " in modul de comunicare " + comm_mode)

def xor_string(s1, s2):
    return "".join([chr(ord(a) ^ ord(b)) for a, b in zip(s1, s2)])

def transport():
    global comm_mode
    global K
    global IV
    global q
    global output
    host_address = socket.gethostname()
    port = 5003

    nodeB = socket.socket()
    nodeB.bind((host_address, port))
    nodeB.listen(2)
    connection, address = nodeB.accept()
    aes = Cryptodome.Cipher.AES.new(K, Cryptodome.Cipher.AES.MODE_ECB)
    block = "blank"
    if comm_mode == "CBC":
        while block!="":
            block = connection.recv(16).decode('ISO-8859-1')
            q=q-1
            block_decrypted = aes.decrypt(block.encode('ISO-8859-1'))
            block_decrypted_xor = xor_string(IV,block_decrypted.decode('ISO-8859-1'))
            IV=block
            output = output + block_decrypted_xor
            print(block_decrypted_xor)
            if q==0:
                q=50
                nodeB.close()
                return None
    elif comm_mode == "OFB":
        while block != "":
            q=q-1
            block = connection.recv(16).decode('ISO-8859-1')
            block_decrypted = aes.encrypt(IV.encode('ISO-8859-1'))
            block_decrypted_xor = xor_string(block,block_decrypted.decode('ISO-8859-1'))
            IV = block_decrypted.decode('ISO-8859-1')
            output = output + block_decrypted_xor
            print(block_decrypted_xor)
            if q==0:
                q=50
                nodeB.close()
                return None
    connection.close()

if __name__ == '__main__':



    line = open("H:\pythonProject\input.txt")
    content = line.read()
    line.close()
    nr = 0
    if len(content) % 16 == 0:
       nr = len(content) // 16
    else:
         nr = len(content) // 16 + 1

    if len(content) % 50 == 0:
        nr = nr // 50
    else:
        nr = nr // 50 + 1
    for i in range(int(nr)):
        nodeB_client_thread()
        nodeB_server_thread()
        transport()

    print(output)
    print(len(output)//16)