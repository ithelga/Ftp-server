import socket
import os


def get_args(params):
    args = ''
    in_brackets = False
    for i in params:
        if i == '[':
            in_brackets = True
        elif i == ']':
            in_brackets = False
        else:
            if i == ' ' and not in_brackets:
                args += "<ImpSpacr>"
            else:
                args += i
    params = args.split("<ImpSpacr>")
    return params


class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()

    def connect_to_server(self):
        self.target_ip = input('Введите IP --> ')
        self.target_port = input('Введите порт --> ')
        self.s.connect((self.target_ip, int(self.target_port)))
        self.main()

    def reconnect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.target_ip, int(self.target_port)))

    def main(self):
        command = input("Введите команду --> ")
        while command != "exit":
            self.s.send(command.encode())
            data_list = command.split(" ")
            if str(data_list[0]) == "copy_from_server" or str(data_list[0]) == "copy_from_client":
                if len(data_list) <= 1:
                    print("Введена неверня команда. Введите help, чтобы изучить функционал")
                else:
                    command, params = command.split(" ", 1)
                    params = ([params.replace('[', '').replace(']', '')])

                if command == "copy_from_server":
                    file_name = str(params[0])
                    confirmation = self.s.recv(1024)
                    if confirmation.decode() == "file-doesn't-exist":
                        print("Файл не найден на сервера")
                    else:
                        write_name = 'from_server ' + file_name
                        if os.path.exists(write_name): os.remove(write_name)
                        with open(write_name, 'wb') as file:
                            while 1:
                                data = self.s.recv(1024)
                                if not data:
                                    break
                                file.write(data)
                        print(file_name, ' успешно скачан.')

                elif command == "copy_from_client":
                    file_name = str(params[0])
                    if not os.path.exists(file_name):
                        print("Файл не найден на клиенте")
                    else:
                        print('Отправка', file_name)
                        if file_name != '':
                            file = open(file_name, 'rb')
                            file_name = file.read(1024)
                            while file_name:
                                self.s.send(file_name)
                                file_name = file.read(1024)
            else:
                answer = self.s.recv(4096)
                print(answer.decode())
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            self.reconnect()
            command = input('Введите команду --> ')
        self.s.close()


client = Client()
