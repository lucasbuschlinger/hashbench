import argparse
import subprocess
from utils import *
from john import *
from hashcat import *

def main():

    #Removing potfiles to have maximum work to do
    subprocess.run(['rm', 'john/run/john.pot'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['rm', 'hashcat/hashcat.potfile'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Initialising parser for CLI parsing
    parser = argparse.ArgumentParser(description="Benchmarking hashcat vs JohnTheRipper")#, usage=usage(), add_help=False)#might wanna write own help

    # Adding arguments to the parser
    ###NOT DONE, ONLY FIRST TRY###
    parser.add_argument('hash', action='store', choices=['md5', 'sha1', 'sha-256', 'sha-512'], help="The hashtype to performe a benchmark on.")
    # Parsing for path to supplied hash file, defaults
    parser.add_argument('mode', type=str, choices=['bruteforce', 'bf', 'wordlist', 'wl'], help="The mode to perform the benchmark on.")
    parser.add_argument('-file', '-f', help="Path to a file containing hash(es)")
    # Parsing for path to supplied rule file
    parser.add_argument('-rules', '-r', help="Path to rule file(s)")
    # Parsing for maximum execution time
    parser.add_argument('-time', '-t', type=int, help="Maximum execution time in minutes")
    # Parsing for minimal password length
    parser.add_argument('-min_len', type=int, help="Minimal password length")
    # Parsing for maximum password length
    parser.add_argument('-max_len', type=int, help="Maximum password length")

    args = parser.parse_args()

    # Calling the utility which maps the input hash to the input needed for the tools
    hash = arg_changer(args.hash)

    # If a maximum execution time was specified in the CLI we convert it from the input minutes to seconds,
    # we do so by mulitplying by 30 as each tool only runs for half of the specified time.
    if(args.time is not None):
        args.time = args.time*30

    # Getting file path or trying to default
    if args.file:
        hash_file = args.file
    else:
        try:
            hash_file = get_default_file(args.hash)
        except Exception as e:
            print(e)
            quit()


    min_len = 4
    max_len = 16

    if(args.min_len):
        min_len = args.min_len
    if(args.max_len):
        max_len = args.max_len

    # Calling the brute force methods and printing the tools speeds
    if args.mode == 'bruteforce' or args.mode == 'bf':
        print("\nRunning brute force benchmark on %s.\n" % args.hash)
        john = john_bruteforce(hash[0], min_len, max_len, hash_file, args.time)
        hashcat = hashcat_bruteforce(hash[1], min_len, max_len, hash_file, args.time)
        print("John's average speed was %fMH/s while cracking %d hashes." % (john[1], john[0]))
        print("Hashcat's average speed was %fMH/s while cracking %d hashes." % (hashcat[1], hashcat[0]))

    # Calling the wordlist methods and printing the tools speeds
    if args.mode == 'wordlist' or args.mode == 'wl':
        print("\nBenchmarking in wordlist mode.\n")
        john = john_wordlist(hash[0], hash_file, "resources/rockyou.wordlist", None, args.time)# wordlist_file)
        hashcat = hashcat_wordlist(hash[1], hash_file, "resources/rockyou.wordlist", args.rules, args.time)#wordlist_file)
        print("John's average speed was %fMH/s while cracking %d hashes." % (john[1], john[0]))
        print("Hashcat's average speed was %fMH/s while cracking %d hashes." % (hashcat[1], hashcat[0]))

# Executing
main()
