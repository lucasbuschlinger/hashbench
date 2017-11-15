import argparse
from utils import *
from john import *
from hashcat import *

def main():

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

#    ##SUBPARSER?
#    # This is the subparser to parse which mode has been selected (mode selection is required)
#    subparsers = parser.add_subparsers(dest='mode', help="The mode to perfome a benchmark on.")
#    subparsers.required = True
#    parser_mode = subparsers.add_parser('mode')
#    # Mutual exclusion so that only one mode gets benchmarked at a time
#    mode_group = parser_mode.add_mutually_exclusive_group(required=True)
#    mode_group.add_argument('-bruteforce', '-bf', action="store_true", help="Selecting a brute force #attack.")
#    mode_group.add_argument('-wordlist', '-wl', action="store_true", help="Selecting a wordlist attack.")


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

    # Calling the brute force methods and printing the tools speeds
    if args.mode == 'bruteforce' or args.mode == 'bf':
        print("\nRunning brute force benchmark on %s.\n" % args.hash)
        john = john_bruteforce(hash[0], 3, 10, hash_file, args.time)
        hashcat = hashcat_bruteforce(hash[1], 3, 10, hash_file, args.time)
        print("John's average speed was %fMH/s." % john)
        print("Hashcat's average speed was %fMH/s." % hashcat)

    # Calling the wordlist methods and printing the tools speeds
    if args.mode == 'wordlist' or args.mode == 'wl':
        print("\nBenchmarking in wordlist mode.\n")
        john = john_wordlist(hash[0], hash_file, "resources/rockyou.wordlist", None, args.time)# wordlist_file)
        hashcat = hashcat_wordlist(hash[1], hash_file, "resources/rockyou.wordlist", args.rules, args.time)#wordlist_file)
        print("John's average speed was %fMH/s." % john)
        print("Hashcat's average speed was %fMH/s." % hashcat)

# Executing
main()
