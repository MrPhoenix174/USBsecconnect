import socket
import ssl
import os
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

SERVER_IP = '192.168.1.1' # IP роутера
PORT = 8443

def get_hwid():
    # Для теста 
    return "USB-SERIAL-123456"

def run_client():
    # Настройка SSL (самоподписанный)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with socket.create_connection((SERVER_IP, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=SERVER_IP) as ssock:
            print("[+] Защищенное соединение установлено")
            
            # 1. Отправляем HWID
            hwid = get_hwid()
            ssock.sendall(hwid.encode())
            
            # 2. Получаем Challenge (Nonce)
            challenge = ssock.recv(1024)
            print(f"[*] Получен вызов: {challenge.hex()}")
            
            # 3. Подписываем ключом с флешки 
            with open("private_key.pem", "rb") as f:
                priv_data = f.read()
                private_key = serialization.load_ssh_private_key(priv_data, password=None)
            
            signature = private_key.sign(challenge)
            ssock.sendall(signature)
            print("[+] Подпись отправлена")

if __name__ == "__main__":
    run_client()
