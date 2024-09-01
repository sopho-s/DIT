import argparse
import networking
import socket
import security

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--ip", help="the ip of the server", type=str, default=socket.gethostbyname(socket.gethostname()))
parser.add_argument("-p", "--port", help="the port of the server", type=int, default=4945)
parser.add_argument("-k", "--key", help="the key file", type=str, default="key.key")
parser.add_argument("-a", "--auth", help="the password hash file if wanted", type=str, default=None)
args = parser.parse_args()

hash: str = None
if args.auth != None:
    with open(args.auth, "r") as f:
        hash = f.read()
connection: networking.ConnectionServer = networking.ConnectionServer(args.ip, args.port, security.GetKeyFile(args.key), hash)
connection.Run()