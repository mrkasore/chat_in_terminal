import socket
import ssl
import threading
import sys

def safe_input(prompt=""):
    print(prompt, end="", flush=True)
    try:
        line = sys.stdin.buffer.readline()
        return line.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        print(f"Ошибка чтения ввода: {e}")
        return ""

def send_message(client, nickname):
    while True:
        msg = f'{nickname}: '+ safe_input()
        client.sendall(msg.encode('UTF-8'))

def get_message(client):
    while True:
        try:
            msg = client.recv(1024).decode('UTF-8')
            print(msg)
        except:
            print("Отключено от сервера.")
            client.close()
            break


def start_client():
    context = ssl.create_default_context()
    context.load_verify_locations("cert.pem")
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED

    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = context.wrap_socket(raw_sock, server_hostname="localhost")
    client.connect(('127.0.0.1', 5555))

    password = input("Введите пароль: ")
    client.send(f"__auth__:{password}".encode("utf-8"))

    response = client.recv(1024).decode("utf-8")

    if response != "__auth_ok__":
        print('Пароль неверный!')
        client.close()
        return

    nickname = safe_input("Введите ваш ник: ")
    print(f"Ваш никнейм - {nickname}")
    thread_send = threading.Thread(target=send_message, args=(client, nickname,))
    thread_send.start()
    thread_get = threading.Thread(target=get_message, args=(client,))
    thread_get.start()

if __name__ == "__main__":
    start_client()

