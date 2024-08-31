import argparse
import encryption
import networking

parser = argparse.ArgumentParser()
parser.add_argument("ip", help="the ip of the server", type=str)
parser.add_argument("-p", "--port", help="the port of the server", type=int, default=4945)
parser.add_argument("-k", "--key", help="the key file", type=str, default="key.key")
parser.add_argument("-q", "--questions", nargs="*", help="the question to be asked to the server", type=str)
parser.add_argument("-s", "--hello", action="store_true", help="if set, before sending a question, the client will test if the server is online with a hello message")
args = parser.parse_args()


connection: networking.ConnectionClient = networking.ConnectionClient(args.ip, args.port, encryption.GetKeyFile(args.key))

if args.hello:
    if connection.CheckServer():
        response: networking.Message = connection.AskQuestions(args.questions)
        if response != None:
            if response.header.err != 0:
                match response.header.err:
                    case 1:
                        print("[-] ERROR: message sent was incorrect or garbage")
                    case 2:
                        print("[-] ERROR: there was an internal error in the server")
                    case 3:
                        print("[-] ERROR: the error is in one of the questions of information")
            for index, info in enumerate(response.info):
                print(f"[*] INFO: question is {args.questions[index]}")
                if info.err != 0:
                    print(f"[-] ERROR: CODE {info.err}")
                else:
                    print(f"[+] RESPONSE IS: {info.data}")
        else:
            print("[*] INFO: no info was given by the server")
    else:
        print("[-] ERROR: server is not accepting connections")
else:
    response: networking.Message = connection.AskQuestions([args.question])
    for info in response.info:
        print(f"[+] RESPONSE {info.index}: {info.data}")