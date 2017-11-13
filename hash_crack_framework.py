import subprocess
import argparse
from utils import *
from bruteforce import *
from wordlist import *

def main():

    #Initialising parser for cli parsing
    parser = argparse.ArgumentParser(description="Benchmarking hashcat vs JohnTheRipper")#might wanna write own help add_help=False)

    #Adding arguments to the parser
    ###NOT DONE, ONLY FIRST TRY###
    parser.add_argument('hash', default='md5', action='store', choices=['md4', 'md5', 'sha1', 'sha-256', 'sha-512'], help="The hashtype to performe a benchmark on.")
    #Parsing for path to supplied hash file, defaults
    parser.add_argument('-file', '-f', help="Path to a file containing hash(es)")
    #Parsing for path to supplied rule file
    parser.add_argument('-rules', '-r', help="Path to rule file(s)")
    #Paring for maximum execution time
    parser.add_argument('-time', '-t', type=int, help="Maximum execution time in seconds")
    #This is the subparser to parse which mode has been selected (mode selection is required)
    subparsers = parser.add_subparsers(dest='mode', help="The mode to perfome a benchmark on.")
    subparsers.required = True
    parser_mode = subparsers.add_parser('mode')
    #Mutual exclusion so that only one mode gets benchmarked at a time
    mode_group = parser_mode.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('-bruteforce', '-bf', action="store_true", help="Selecting a brute force attack.")
    mode_group.add_argument('-wordlist', '-wl', action="store_true", help="Selecting a wordlist attack.")


    args = parser.parse_args()

    #Calling the utility which maps the input hash to the input needed for the tools
    hash = arg_changer(args.hash)

    #Getting file path or trying to default
    if args.file:
        hash_file = args.file
    else:
        try:
            hash_file = get_default_file(args.hash)
        except Exception as e:
            print(e)
            quit()

    ############
    ##DEPRECATED
    ############
    #Calling integrated benchmarks
    #if args.b:
    #    print("Running integrated benchmarks on %s.\n" % args.hash)
    #    process = subprocess.Popen(["./john/run/john", "--test", "--format={}".format(hash[0])], stdout=subprocess.PIPE)
    #    print("###########")
    #    while(process.poll() == None):
    #        out, err = process.communicate()
    #        print(out)
    #    print("###########")
    #    subprocess.run(["./hashcat/hashcat", "-m", hash[1], "-b"])

    #Calling the brute force methods with hashtype, minimum and maximum password length
    if args.bruteforce:
        print("\nRunning brute force benchmark on %s.\n" % args.hash)
        john = john_bruteforce(hash[0], 4, 5, hash_file)
        hashcat = hashcat_bruteforce(hash[1], 4, 5, hash_file)
        print("John's average speed was %fMH/s." % john)
        print("Hashcat's average speed was %fMH/s." % hashcat)

    if args.wordlist:
        print("\nBenchmarking in wordlist mode.\n")
        john = john_wordlist(hash[0], hash_file, "resources/rockyou.wordlist", "KoreLogicRules", args.time/2)# wordlist_file)
        hashcat = hashcat_wordlist(hash[1], hash_file, "resources/rockyou.wordlist", args.rules, args.time/2)#wordlist_file)
        print("John's average speed was %fMH/s." % john)
        print("Hashcat's average speed was %fMH/s." % hashcat)

#Executing
main()
