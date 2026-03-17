import socket
import threading

board = []
server_running = True
active_clients = []
clients_lock = threading.Lock()
print_lock = threading.Lock()

def server_commands():
    global server_running
    while server_running:
        cmd = input().strip()
        if cmd == "off":
            with print_lock:
                print("(*) ВЫКЛЮЧЕНИЕ СЕРВЕРА!!")
            server_running = False
            break

def handle_client(conn, addr):
    global server_running
    with clients_lock:
        active_clients.append(conn)
    try:
        while server_running:
            try:
                conn.settimeout(0.5)
                try:
                    data = conn.recv(1024).decode().strip()
                except socket.timeout:
                    continue
                if not data:
                    break
                with print_lock:
                    print(f"(+) ПОЛУЧЕНО от {addr}: {data}")
                if data.lower() == "exit":
                    conn.send("(*) ДО СВИДАНИЯ!".encode())
                    break
                parts = data.split(' ', 2)
                command = parts[0].upper()
                if command == "PUB":
                    if len(parts) != 3:
                        conn.send("(?) ОШИБКА: pub <текст>".encode())
                        continue
                    author, message = parts[1], parts[2]
                    if not message.strip():
                        conn.send("(?) ОШИБКА: ВВЕДИТЕ ТЕКСТ".encode())
                        continue
                    board.append((author, message))
                    conn.send("(+) ОТПРАВЛЕНО!".encode())

                elif command == "ADS":
                    if len(parts) != 2:
                        conn.send("(?) ОШИБКА: ads <число>".encode())
                        continue
                    try:
                        n = int(parts[1])
                        if n <= 0:
                            conn.send("(?) ОШИБКА: ЧИСЛО ДОЛЖНО БЫТЬ БОЛЬШЕ 0".encode())
                            continue
                        recent = board[-n:] if board else []
                        if not recent:
                            conn.send("( ) ПУСТО..".encode())
                        else:
                            response = "\n".join([f"(+) {a}: {t}" for a, t in recent]) + "\n"
                            conn.send(response.encode())
                    except ValueError:
                        conn.send("(?) ОШИБКА: ВВЕДИТЕ ЧИСЛО".encode())
                else:
                    conn.send("(?) ОШИБКА: pub, ads, exit".encode())
            except:
                break
    finally:
        with clients_lock:
            if conn in active_clients:
                active_clients.remove(conn)
        conn.close()

def main():
    global server_running
    host = "127.0.0.1"
    port = 9090
    threading.Thread(target=server_commands, daemon=True).start()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    with print_lock:
        print(f"СЕРВЕР ЗАПУЩЕН ==> {host}:{port}")
        print("(*) off - выключить")
        print("(...) ОЖИДАНИЕ ПОДКЛЮЧЕНИЙ...")

    while server_running:
        try:
            server.settimeout(0.5)
            try:
                conn, addr = server.accept()
                with print_lock:
                    print(f"\n(=) КЛИЕНТ {addr} ПОДКЛЮЧИЛСЯ")
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                continue
        except:
            pass
    for client in active_clients[:]:
        try:
            client.send("(*) СЕРВЕР ЗАКРЫВАЕТСЯ!".encode())
            client.close()
        except:
            pass
    server.close()
    with print_lock:
        print("(*) ДО СВИДАНИЯ!")

main()