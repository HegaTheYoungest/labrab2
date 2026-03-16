import socket
import sys


board = []

def main():
    host = "127.0.0.1"
    port = 9090
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Создание сокета
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #удаление кд на пересоздание сервера
    server.bind((host, port)) #связывание хоста и айпишника
    server.listen(1) #чтобы сервер стал открытым к запросам

    print(f"СЕРВЕР ЗАПУЩЕН НА ==> {host}:{port}"
          "\nДОБРО ПОЖАЛОВАТЬ НА ДОСКУ ОБЪЯВЛЕНИЙ!!"
          "\nВЕДИТЕ СЕБЯ ДОБРОЖЕЛАТЕЛЬНО - иначе БАН!!"
          "\nФЛУД ЗАПРЕЩЕН - карается БАНОМ!!"
          "\nСКАМ,ВОРОВСТВО - БАН, ВЫЧИСЛЕНИЕ ПО АЙПИ")

    try:
        while True:
            print("\nОЖИДАНИЕ ПОДКЛЮЧЕНИЯ...")
            conn, addr = server.accept() #принятие запросов
            print(f"КЛИЕНТ {addr} ПОДКЛЮЧИЛСЯ")
            try:
                while True:
                    data = conn.recv(1024).decode().strip() #создание буфера в 1024 байта чтобы хранить информацию (передается двоичный код и ты это декодируешь)
                    if not data:
                        break
                    print(f"ПОЛУЧЕНО: {data}")
                    parts = data.split(' ', 2)
                    command = parts[0].upper()
                    if command in ["PUB"]:
                        if len(parts) != 3:
                            conn.send("ОШИБКА: Используйте: pub <Ваш текст>".encode())
                            continue
                        author = parts[1]
                        message = parts[2]
                        if not message.strip():
                            conn.send("ОШИБКА: Введите текст".encode())
                            continue
                        board.append((author, message))
                        conn.send("ОТПРАВЛЕНО".encode())
                        print(f"ДОБАВЛЕНО: {author}: {message[:30]}...")
                    elif command in ["ADS"]:
                        if len(parts) != 2:
                            conn.send("ОШИБКА: Используйте: ads <Ваше число>".encode())
                            continue
                        try:
                            n = int(parts[1])
                            if n <= 0:
                                conn.send("ОШИБКА: Число должно быть больше нуля".encode())
                                continue
                            recent = board[-n:] if board else []
                            if not recent:
                                conn.send("ПУСТО..".encode())
                            else:
                                response = "\n".join([f"{nickname}: {text}" for nickname, text in recent]) + "\n"
                                conn.send(response.encode())
                        except ValueError:
                            conn.send("ОШИБКА: Нужно ввести число".encode())
                    else:
                        conn.send("ОШИБКА: Команды: pub, ads, exit".encode())
            except ConnectionResetError:
                print(f"Клиент {addr} отключился")
            except Exception as e:
                print(f"ОШИБКА: {e}")
            finally:
                conn.close()
                print(f"Клиент {addr} отключен")
    except KeyboardInterrupt:
        print("Сервер остановлен")
    finally:
        server.close()

main()