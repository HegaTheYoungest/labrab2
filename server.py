import socket
import sys
import threading

board = []
server_running = True
active_clients = []
clients_lock = threading.Lock()

def server_commands():
    global server_running
    while server_running:
        try:
            cmd = input("{=}> ").strip()
            if cmd == "off":
                print("\n(=) ВЫКЛЮЧЕНИЕ СЕРВЕРА!!!!!")
                server_running = False
                break
        except:
            break

def disconnect_all_clients():
    global active_clients
    with clients_lock:
        for client in active_clients[:]:
            try:
                if client:
                    try:
                        client.send("(=) СЕРВЕР ЗАКРЫВАЕТСЯ!".encode())
                    except:
                        pass
                    try:
                        client.close()
                    except:
                        pass
            except:
                pass
        active_clients.clear()

def handle_client(conn, addr):
    global server_running
    with clients_lock:
        active_clients.append(conn)
    try:
        while server_running:
            try:
                if not conn:
                    break
                conn.settimeout(0.5)
                try:
                    data = conn.recv(1024).decode().strip()
                except socket.timeout:
                    continue
                except (ConnectionResetError, ConnectionAbortedError):
                    break
                except:
                    break
                if not data:
                    break
                print(f"(=) ПОЛУЧЕНО от {addr}: {data}")
                if data.lower() == "exit":
                    try:
                        conn.send("(=) ДО СВИДАНИЯ!".encode())
                    except:
                        pass
                    break
                parts = data.split(' ', 2)
                command = parts[0].upper()
                if command in ["PUB"]:
                    if len(parts) != 3:
                        try:
                            conn.send("(=) ОШИБКА: Используйте: pub <Ваш текст>".encode())
                        except:
                            pass
                        continue
                    author = parts[1]
                    message = parts[2]
                    if not message.strip():
                        try:
                            conn.send("(=) ОШИБКА: ВВЕДИТЕ ТЕКСТ".encode())
                        except:
                            pass
                        continue
                    board.append((author, message))
                    try:
                        conn.send("(=) ОТПРАВЛЕНО!".encode())
                    except:
                        pass
                    print(f"(=) ДОБАВЛЕНО: {author}: {message[:30]}...")
                elif command in ["ADS"]:
                    if len(parts) != 2:
                        try:
                            conn.send("(=) ОШИБКА: Используйте: ads <Ваше число>".encode())
                        except:
                            pass
                        continue
                    try:
                        n = int(parts[1])
                        if n <= 0:
                            try:
                                conn.send("(=) ОШИБКА: ЧИСЛО ДОЛЖНО БЫТЬ БОЛЬШЕ НУЛЯ".encode())
                            except:
                                pass
                            continue
                        recent = board[-n:] if board else []
                        if not recent:
                            try:
                                conn.send("(=) ПУСТО..".encode())
                            except:
                                pass
                        else:
                            response = "\n".join([f"(=) {nickname}: {text}" for nickname, text in recent]) + "\n"
                            try:
                                conn.send(response.encode())
                            except:
                                pass
                    except ValueError:
                        try:
                            conn.send("(=) ОШИБКА: НУЖНО ВВЕСТИ ЧИСЛО".encode())
                        except:
                            pass
                else:
                    try:
                        conn.send("(=) ОШИБКА: Команды: pub, ads, exit".encode())
                    except:
                        pass
            except Exception as e:
                print(f"(=) ОШИБКА ПРИ ОБРАБОТКЕ КЛИЕНТА {addr}: {e}")
                break
    except Exception as e:
        print(f"(=) ОШИБКА: {e}")
    finally:
        with clients_lock:
            if conn in active_clients:
                try:
                    active_clients.remove(conn)
                except:
                    pass
        try:
            if conn:
                conn.close()
        except:
            pass
        print(f"(=) КЛИЕНТ {addr} ОТКЛЮЧЕН!")

def main():
    global server_running
    host = "127.0.0.1"
    port = 9090
    cmd_thread = threading.Thread(target=server_commands)
    cmd_thread.daemon = True
    cmd_thread.start()
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)

        print(f"(=) СЕРВЕР ЗАПУЩЕН НА ==> {host}:{port}"
              "\n(=) КОМАНДА СЕРВЕРА:"
              "\n(=) off - выключение сервера")
        print("\n\n(=) ОЖИДАНИЕ ПОДКЛЮЧЕНИЙ...")

        while server_running:
            try:
                server.settimeout(0.5)
                try:
                    conn, addr = server.accept()
                    print(f"\n(=) КЛИЕНТ {addr} ПОДКЛЮЧИЛСЯ")

                    client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if server_running:
                        print(f"(=) ОШИБКА: {e}")
            except Exception as e:
                print(f"(=) ОШИБКА: {e}")
    except Exception as e:
        print(f"(=) ОШИБКА: {e}")
    finally:
        print("\n(=) ЗАВЕРШЕНИЕ РАБОТЫ СЕРВЕРА...")
        disconnect_all_clients()
        try:
            if server:
                server.close()
                print("\n(=) СЕРВЕРНЫЙ СОКЕТ ЗАКРЫТ")
        except:
            pass
        print("\n(=) ДО СВИДАНИЯ!")


if __name__ == "__main__":
    main()