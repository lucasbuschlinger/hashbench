import subprocess
import argparse
from usage import *
from utils import *
from bruteforce import *

def main():

    #Initialising parser for cli parsing
    parser = argparse.ArgumentParser(description='Hash Crack Framework')

    #Adding arguments to the parser
    ###NOT DONE, ONLY FIRST TRY###
    parser.add_argument('-b', action='store_true', default=False)
    parser.add_argument('-hash', default='md5', choices=['md4', 'md5', 'sha1', 'sha-256', 'sha-512'])
    parser.add_argument('-bruteforce', action='store_true', default=False)
    args = parser.parse_args()

    #Calling the utility which maps the input hash to the input needed for the tools
    hash = arg_changer(args.hash)

    ############
    ##DEPRECATED
    ############
    #Calling integrated benchmarks
    if args.b:
        print("Running integrated benchmarks on %s.\n" % args.hash)
        process = subprocess.Popen(["./john/run/john", "--test", "--format={}".format(hash[0])], stdout=subprocess.PIPE)
        print("###########")
        while(process.poll() == None):
            out, err = process.communicate()
            print(out)
        print("###########")
        subprocess.run(["./hashcat/hashcat", "-m", hash[1], "-b"])

    #Calling the brute force methods with hashtype, minimum and maximum password length
    if args.bruteforce:
        print("Running brute force benchmark on %s.\n" % args.hash)
        john = john_bruteforce(hash[0], 4, 5)
        hashcat = hashcat_bruteforce(hash[1], 4, 5)
        print("John's speed was %fMH/s." % john)
        print("Hashcat's speed was %fMH/s." % hashcat)


#Executing
main()
