import socket

def main():
    host = "127.0.0.1"
    port = 9090
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        print(f"ПОДКЛЮЧЕНО К СЕРВЕРУ ==> {host}:{port}"
              "\n(=) ДОБРО ПОЖАЛОВАТЬ НА ДОСКУ ОБЪЯВЛЕНИЙ!!"
              "\n(=) ВЕДИТЕ СЕБЯ ДОБРОЖЕЛАТЕЛЬНО - иначе БАН!!"
              "\n(=) ФЛУД ЗАПРЕЩЕН - карается БАНОМ!!"
              "\n(=) СКАМ,ВОРОВСТВО - БАН, ВЫЧИСЛЕНИЕ ПО АЙПИ!!")
    except ConnectionRefusedError:
        print("(?) ОШИБКА: Сервер не запущен")
        return
    name = input("\n(..) Введите ваш никнейм!"
                 "\n(..) Если два слова и более, используйте нижнее подчеркивание. Если не хотите вводить ник, просто нажмите enter: ").strip()
    if not name:
        name = "Анонимный_пользователь"

    print("\n ========================КОМАНДЫ========================:")
    print("(1) pub <Ваш текст> - Опубликовать объявление!")
    print("(2) ads <Число> - Показать последнее кол-во объявлений!")
    print("(3) exit - Выход!")

    exited = False
    try:
        while True:
            cmd = input("{=}> ").strip()
            if not cmd:
                continue
            if cmd.lower() == "exit":
                exited = True
                try:
                    client.send("exit".encode())
                    response = client.recv(4096).decode().strip()
                    print(response)
                except:
                    pass
                break
            if cmd.upper().startswith("PUB"):
                parts = cmd.split(' ', 1)
                if len(parts) == 2:
                    full_cmd = f"pub {name} {parts[1]}"
                else:
                    print("(?) ОШИБКА: Используйте: pub <Ваш текст>")
                    continue
            else:
                full_cmd = cmd
            try:
                client.send(full_cmd.encode())
                client.settimeout(2.0)
                try:
                    response = client.recv(4096).decode().strip()
                    if not response:
                        print("\n(*) СЕРВЕР ЗАКРЫЛ СОЕДИНЕНИЕ")
                        break
                    print(response)
                except socket.timeout:
                    print("(...) ОЖИДАНИЕ ОТВЕТА ОТ СЕРВЕРА..")
                    continue
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                print("(*) СОЕДИНЕНИЕ С СЕРВЕРОМ ПОТЕРЯНО")
                break
            except Exception as e:
                print(f"(?) ОШИБКА: {e}")
                break
    except KeyboardInterrupt:
        print("(*) ВЫХОД..")
    finally:
        try:
            client.close()
        except:
            pass
        if not exited:
            print("(*) ДО СВИДАНИЯ!")

main()