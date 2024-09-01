import security
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("password", help="the password", type=str)
parser.add_argument("-o", "--output", help="the file to output to", type=str, default="pass.hash")
args = parser.parse_args()

with open(args.output, "w") as f:
    f.write(security.PasswordHash(args.password))