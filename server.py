import os
import socket
import ssl
import threading
from dotenv import load_dotenv

load_dotenv()

RIGHT_PASSWORD = os.getenv('RIGHT_PASSWORD')
clients = []

def send_msg_to_clients(conn, msg):
    for client in clients:
        try:
            if client != conn:
                client.send(msg)
        except:
            clients.remove(client)
            client.close()

def start_one_client(conn):
    try:
        data_password = conn.recv(1024).decode('utf-8')
        password_lst = data_password.split(':')
        password = password_lst[1]
        if password == RIGHT_PASSWORD:
            conn.send("__auth_ok__".encode('utf-8'))
        else:
            conn.close()
    except:
        conn.close()

    while True:
        try:
            msg = conn.recv(1024)
            send_msg_to_clients(conn, msg)
            print(msg.decode('UTF-8'))
        except:
            conn.close()
            break

def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 5555))
    server.listen()
    print(f"Сервер ('127.0.0.1', 5555) запущен!")

    while True:
        raw_conn, addr = server.accept()
        try:
            conn = context.wrap_socket(raw_conn, server_side=True)
            clients.append(conn)
            print(f'Произошло подключение - {addr}')
            thread = threading.Thread(target=start_one_client, args=(conn,))
            thread.start()
        except ssl.SSLError as e:
            print(f"SSL ошибка при подключении: {e}")
            raw_conn.close()

if __name__ == "__main__":
    start_server()

