import argparse
import networking
import socket
import encryption

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--ip", help="the ip of the server", type=str, default=socket.gethostbyname(socket.gethostname()))
parser.add_argument("-p", "--port", help="the port of the server", type=int, default=4945)
parser.add_argument("-k", "--key", help="the key file", type=str, default="key.key")
args = parser.parse_args()

connection: networking.ConnectionServer = networking.ConnectionServer(args.ip, args.port, encryption.GetKeyFile(args.key))
connection.Run()