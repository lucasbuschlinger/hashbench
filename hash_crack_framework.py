import subprocess
import argparse
from usage import *
from utils import *
from bruteforce import *

def main():

    parser = argparse.ArgumentParser(description='Hash Crack Framework')
    parser.add_argument('-b', action='store_true', default=False)
    parser.add_argument('-hash', default='md5', choices=['md4', 'md5', 'sha1', 'sha-256', 'sha-512'])
    args = parser.parse_args()

    hash = arg_changer(args.hash)

    if args.b:
        print("Running integrated benchmarks on %s.\n" % args.hash)
        process = subprocess.Popen(["./john/run/john", "--test", "--format={}".format(hash[0])], stdout=subprocess.PIPE)
        print("###########")
        while(process.poll() == None):
            out, err = process.communicate()
            print(out)
        print("###########")
        subprocess.run(["./hashcat/hashcat", "-m", hash[1], "-b"])

main()
