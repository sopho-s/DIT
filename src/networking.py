import socket
import random
import infominer
import encryption
import json

class Header:
    def __init__(self, hello: bool = False, help: bool = False, err: int = 0, infocount: int = 0, questioncount: int = 0, size: int = 0):
        self.hello: bool = hello
        self.help: bool = help
        self.err: int = err
        self.infocount: int = infocount
        self.questioncount: int = questioncount
        self.size: int = size
    def GetBytes(self) -> bytes:
        message: bytes = b""
        flags: int = 2 ** 7 if self.hello else 0
        flags += 2 ** 6 if self.help else 0
        message += flags.to_bytes(1, "big")
        message += (self.err * 2 ** 4).to_bytes(1, "big")
        message += self.infocount.to_bytes(2, "big")
        message += self.questioncount.to_bytes(2, "big")
        message += self.size.to_bytes(2, "big")
        return message
    
class Body:
    def __init__(self, index: int = None, err: int = 0, data: str = None):
        self.index: int = index
        self.err: int = err
        if data != None:
            self.datasize: int = len(data)
        else:
            self.datasize: int = 0
        self.data: str = data
    def GetBytes(self) -> bytes:
        message: bytes = b""
        if self.index != None:
            message += self.index.to_bytes(2, "big")
        message += (self.err * 2 ** 4).to_bytes(1, "big")
        message += b"\x00"
        message += self.datasize.to_bytes(2, "big")
        if self.data != None:
            message += self.data.encode("ascii")
        return message

class Message:
    def __init__(self, header: Header, info: list[Body] = [], questions: list[Body] = []):
        self.header: Header = header
        self.info: list[Body] = info
        self.questions: list[Body] = questions
    def GetBytes(self, key: bytes) -> bytes:
        message: bytes = b""
        for question in self.questions:
            message += question.GetBytes()
        for info in self.info:
            message += info.GetBytes()
        if message != b"":
            message = encryption.Encrypt(key, message)
        self.header.size = len(message)
        message = self.header.GetBytes() + message
        return message
    
def GetHeader(message: bytes) -> tuple[Header, bytes]:
    hello: bool = True if int.from_bytes(message[0:1], "big") & 0b10000000 != 0 else False
    help: bool = True if int.from_bytes(message[0:1], "big") & 0b01000000 != 0 else False
    error: int = int(int.from_bytes(message[1:2], "big") * 2 ** -4)
    infocount: int = int.from_bytes(message[2:4], "big")
    questioncount: int = int.from_bytes(message[4:6], "big")
    size: int = int.from_bytes(message[6:8], "big")
    return (Header(hello, help, error, infocount, questioncount, size), message[8:])

def GetBody(message: bytes, isquestion: bool) -> tuple[Header, bytes]:
    if isquestion:
        error: int = int(int.from_bytes(message[0:1], "big") * 2 ** -4)
        datasize: int = int.from_bytes(message[2:4], "big")
        data = message[4:4+datasize].decode("ascii")
        return (Body(None, error, data), message[4+datasize:])
    index: int = int.from_bytes(message[0:2], "big")
    error: int = int(int.from_bytes(message[2:3], "big") * 2 ** -4)
    datasize: int = int.from_bytes(message[4:6], "big")
    data = message[6:6+datasize].decode("ascii")
    return (Body(index, error, data), message[6+datasize:])

def InterpretMessage(message: bytes, key: bytes) -> Message:
    header, message = GetHeader(message)
    infolist: list[Body] = []
    questionlist: list[Body] = []
    if len(message) != 0:
        message = encryption.Decrypt(key, message)
        for _ in range(header.infocount):
            info, message = GetBody(message, False)
            infolist.append(info)
        for _ in range(header.questioncount):
            question, message = GetBody(message, True)
            questionlist.append(question)
    return Message(header, infolist, questionlist)

def InterpretMessagePostHeader(message: bytes, header: Header, key: bytes) -> Message:
    infolist: list[Body] = []
    questionlist: list[Body] = []
    if len(message) != 0:
        message = encryption.Decrypt(key, message)
        for _ in range(header.infocount):
            info, message = GetBody(message, False)
            infolist.append(info)
        for _ in range(header.questioncount):
            question, message = GetBody(message, True)
            questionlist.append(question)
    return Message(header, infolist, questionlist)

def recvall(sock, size):
    result = b''
    remaining = size
    while remaining > 0:
        data = sock.recv(remaining)
        result += data
        remaining -= len(data)
    return result

class ConnectionClient:
    def __init__(self, ip: str, port: int, key: bytes):
        self.ip: str = ip
        self.port: int = port
        self.key: bytes = key
    def CheckServer(self) -> bool:
        self.connection: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.ip, self.port))
        self.connection.sendall(Message(Header(True)).GetBytes(self.key))
        self.connection.settimeout(10)
        data = recvall(self.connection, 8)
        self.connection.close()
        if data == b"":
            return False
        message: Message = InterpretMessage(data, self.key)
        if message.header.hello:
            return True
        else:
            return False
    def AskQuestions(self, questionsstr: list[str]) -> Message:
        questions: list[Body] = []
        for question in questionsstr:
            questions.append(Body(data = question))
        self.connection: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.ip, self.port))
        self.connection.sendall(Message(Header(questioncount = len(questions)), questions = questions).GetBytes(self.key))
        self.connection.settimeout(10)
        data: bytes = recvall(self.connection, 8)
        header, _ = GetHeader(data)
        data: bytes = recvall(self.connection, header.size)
        self.connection.close()
        if data == b"":
            return None
        message: Message = InterpretMessagePostHeader(data, header, self.key)
        return message
    def GetHelp(self) -> Message:
        self.connection: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.ip, self.port))
        self.connection.sendall(Message(Header(help = True)).GetBytes(self.key))
        self.connection.settimeout(10)
        data: bytes = recvall(self.connection, 8)
        header, _ = GetHeader(data)
        data: bytes = recvall(self.connection, header.size)
        self.connection.close()
        if data == b"":
            return None
        message: Message = InterpretMessagePostHeader(data, header, self.key)
        return message

class ConnectionServer:
    def __init__(self, ip: str, port: int, key: bytes):
        self.ip: str = ip
        self.port: int = port
        self.key: bytes = key
    def List(self) -> list[str]:
        with open("help.json", "r") as f:
            help: dict = json.loads(f.read())
        commands: list[str] = []
        for command in help["commands"]:
            name: str = command["name"]
            description: str = command["description"]
            commands.append(f"{name} {description}")
        return commands
    def Process(self, message: Message) -> Message:
        hello = message.header.hello
        if message.header.help == True:
            commands: list[str] = self.List()
            info: list[Body] = []
            for command in commands:
                info.append(Body(index = 0, data = command))
            return Message(Header(hello, infocount = len(info)), info)
        else:
            error: int = 0
            responses: list[Body] = []
            for index, question in enumerate(message.questions):
                response: str = infominer.ProcessQuestion(question.data)
                if response == None:
                    error = 3
                    responses.append(Body(index, 1, response))
                else:
                    responses.append(Body(index, 0, response))
            return Message(Header(hello = hello, infocount = len(message.questions), err = error), responses)
    def Run(self):
        self.connection: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.bind((self.ip, self.port))
        while True:
            self.connection.listen()
            conn, addr = self.connection.accept()
            data: bytes = recvall(conn, 8)
            header, _ = GetHeader(data)
            data: bytes = recvall(conn, header.size)
            message: Message = InterpretMessagePostHeader(data, header, self.key)
            message = self.Process(message)
            conn.sendall(message.GetBytes(self.key))
