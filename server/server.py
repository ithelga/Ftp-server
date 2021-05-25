import socket
import threading
import os
import pathlib
from mycommand import Command
from myfeatures import create_folder, create_file, delete, write_to_file, read_file, rename, copy, move, help, \
    change_root, change_dir_down, change_dir_up, get_list, get_root, start, get_ans, get_args


class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.accept_connections()

    def accept_connections(self):
        ip = socket.gethostbyname(socket.gethostname())
        port = int(input('Enter desired port --> '))

        self.s.bind((ip, port))
        self.s.listen(100)

        print('Running on IP: ' + ip)
        print('Running on port: ' + str(port))

        way = input('Рабочая директория --> ')
        start(way)

        while True:
            c, addr = self.s.accept()
            threading.Thread(target=self.handle_client, args=(c, addr,)).start()

    def handle_client(self, c, addr):
        data = c.recv(1024).decode()
        data_list = data.split(" ")
        if len(data_list) < 1:
            ans = get_ans("Введена неверня команда. Введите help, чтобы изучить функционал")
            c.send(ans.encode())
        if len(data_list) == 1:
            command = data
            params = data_list[1:]
        else:
            command, params = data.split(" ", 1)
            params = get_args(params)

        if command in MAP:
            ans = get_ans(MAP[command].execute(params))
            c.send(ans.encode())
        if command == "copy_from_server":
            print(params[0])
            file_name = (get_root().joinpath(pathlib.Path(params[0])))
            if not os.path.exists(file_name):
                c.send("file-doesn't-exist".encode())

            else:
                c.send("file-exists".encode())
                print('Sending', file_name)
                if file_name != '':
                    file = open(file_name, 'rb')
                    file_name = file.read(1024)
                    while file_name:
                        c.send(file_name)
                        file_name = file.read(1024)

        if command == "copy_from_client":
            print("Getting file from client")
            file_name = params[0]
            write_name = 'from_client ' + file_name

            write_name = (get_root().joinpath(pathlib.Path(write_name)))
            if os.path.exists(write_name):
                os.remove(write_name)
            with open(write_name, 'wb') as file:
                while 1:
                    data = c.recv(1024)
                    if not data:
                        break
                    file.write(data)
            print(file_name, 'successfully downloaded.')

        else:
            ans = get_ans("Введена неверня команда. Введите help, чтобы изучить функционал")
            c.send(ans.encode())

        c.shutdown(socket.SHUT_RDWR)
        c.close()


if __name__ == '__main__':
    cfile = Command(create_file)
    cfolder = Command(create_folder)
    delete = Command(delete)
    wfile = Command(write_to_file)
    rfile = Command(read_file)
    renamef = Command(rename)
    cp = Command(copy)
    mv = Command(move)
    hp = Command(help)
    list = Command(get_list)
    chroot = Command(change_root)
    chdirup = Command(change_dir_up)
    chdirdown = Command(change_dir_down)

    MAP = {
        'create_file': cfile,
        'create_folder': cfolder,
        'delete': delete,
        'write_to_file': wfile,
        'read_file': rfile,
        'rename': renamef,
        'copy': cp,
        'move': mv,
        'help': hp,
        'change_root': chroot,
        'change_dir_up': chdirup,
        'change_dir_down': chdirdown,
        'list': list,
    }
    server = Server()
