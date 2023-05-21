from socket import *
from threading import *

clients = []
names = []


def client_thread(cli):
    flag = True
    while True:
        try:
            message = cli.recv(1024).decode('utf8')
            if flag:
                names.append(message)
                print(message, 'connected')
                cli.send(("Other users:" + ','.join(names)).encode('utf8'))
                flag = False
            for c in clients:
                if c != cli:
                    index = clients.index(cli)
                    name = names[index]
                    if name == message:
                        c.send(("new_client-"+name).encode('utf8'))
                    else:
                        c.send((name + '--' + message).encode('utf8'))
        except:
            index = clients.index(cli)
            clients.remove(cli)
            name = names[index]
            names.remove(name)
            for c in clients:
                c.send(("exit_client-" + name).encode('utf8'))
            print(name + ' exit')
            break


server = socket(AF_INET, SOCK_STREAM)

ip = '127.0.0.1'
port = 55555
server.bind((ip, port))
server.listen()
print('Server is listening...')

while True:
    client, address = server.accept()
    clients.append(client)
    print('Server connected..', address[0] + ':' + str(address[1]))
    thread = Thread(target=client_thread, args=(client,))
    thread.start()
