import socket
import os
import Cryptodome.Cipher.AES

K1 = "" #CBC
K2 = "" #OFB
K3 = "A%D*G-KaPdSgVkYp" #cheie utilizata in criptarea cheilor


def nodeKM_thread():
    global K1
    global K2
    K1 = os.urandom(16).decode('ISO-8859-1')
    K2 = os.urandom(16).decode('ISO-8859-1')
    host_address = socket.gethostname()

    port = 5001
    KM = socket.socket()
    KM.bind((host_address, port))
    KM.listen(2)
    connection, address = KM.accept()
    print("S-a connectat ")

    message_nodeKM = "Ce metoda de criptare doriti sa folositi ?\n "
    connection.send(message_nodeKM.encode())
    message_nodeA = connection.recv(3).decode()
    print("Modul de criptare ales este " + message_nodeA)
    if message_nodeA=="CBC":
        aes = Cryptodome.Cipher.AES.new(K3.encode('ISO-8859-1'), Cryptodome.Cipher.AES.MODE_ECB)
        K1_encrypted = aes.encrypt(K1.encode('ISO-8859-1'))
        print("Cheia K1: "+ K1 + " a fost criptata folosind Aes ===> " + K1_encrypted.decode('ISO-8859-1'))
        message_nodeKM= K1_encrypted
        connection.send(message_nodeKM)
    else:

        aes = Cryptodome.Cipher.AES.new(K3.encode('ISO-8859-1'), Cryptodome.Cipher.AES.MODE_ECB)
        K2_encrypted = aes.encrypt(K2.encode('ISO-8859-1'))
        print("Cheia K2: " + K2 + " a fost criptata folosind Aes ===> " + K2_encrypted.decode('ISO-8859-1'))
        message_nodeKM = K2_encrypted
        connection.send(message_nodeKM)

    connection.close()

if __name__ == '__main__':
    line=open("H:\pythonProject\input.txt")
    content = line.read()
    line.close()
    nr = 0
    if len(content) % 16 == 0:
        nr = len(content)//16
    else:
        nr = len(content)//16 + 1

    if len(content) % 50 == 0:
        nr = nr // 50
    else:
        nr = nr // 50 + 1
    for i in range(int(nr)):
        nodeKM_thread()

