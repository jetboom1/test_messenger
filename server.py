from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class Client(Protocol):
    ip: str = None
    login: str = None
    factory: 'Chat'

    def __init__(self, factory):
        """
        Инициализация фабрики клиента
        :param factory:
        """
        self.factory = factory

    def connectionMade(self):
        """
        Обработчик подключения нового клиента
        """
        self.ip = self.transport.getHost().host
        self.factory.clients.append(self)
        print(f"Client connected: {self.ip}\n")
        #self.factory.notify_all_users(f'New user {self.login} has been connected\n')
        self.transport.write("Welcome to the chat buddy\n".encode())
        for message in self.factory.messagesList:
            self.transport.write((message+'\n').encode())

    def dataReceived(self, data: bytes):
        """
        Обработчик нового сообщения от клиента
        :param data:
        """
        message = data.decode().replace('\n', '')
        if self.login is not None:
            server_message = f'{self.login}: {message}'
            self.factory.notify_all_users(server_message+'\n')
            self.factory.messagesList.append(server_message)
            print(server_message)
        else:
            if message.startswith('login:'):
                self.login = message.replace('login:', '')
                if self.login in self.factory.loginList:
                    self.transport.write('login is busy'.encode())
                else:
                    self.factory.loginList.append(self.login)
                    notification = f"New user connected: {self.login}\n"
                    self.factory.notify_all_users(notification)
                    print(notification)
            else:
                print('invalid login\n')

    def connectionLost(self, reason=None):
        """
        Обработчик отключения клиента
        :param reason:
        """
        self.factory.clients.remove(self)
        self.factory.notify_all_users(f"User disconnected: {self.login}\n")
        print(f"Client disconnected: {self.ip}\n")


class Chat(Factory):
    clients: list
    loginList: list = []
    messagesList: list = []

    def __init__(self):
        """
        Инициализация сервера
        """
        self.clients = []
        print("*" * 10, "\nStart server \nCompleted [OK]")

    def startFactory(self):
        """
        Запуск процесса ожидания новых клиентов
        :return:
        """
        print("\n\nStart listening for the clients...\n")

    def buildProtocol(self, addr):
        """
        Инициализация нового клиента
        :param addr:
        :return:
        """
        return Client(self)

    def notify_all_users(self, data: str):
        """
        Отправка сообщений всем текущим пользователям
        :param data:
        :return:
        """
        for user in self.clients:
            user.transport.write((data+'\n').encode())


if __name__ == '__main__':

    reactor.listenTCP(7410, Chat())
    reactor.run()