import encryption
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("key", help="the name of the key file", type=str)
args = parser.parse_args()

encryption.GenerateKeyFile(args.key)