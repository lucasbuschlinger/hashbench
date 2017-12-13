import argparse
import subprocess
from modules.utils import *
from modules.hashcat import *
from modules.john import *


# noinspection SpellCheckingInspection
def main():
    # Removing potfiles to have maximum work to do
    subprocess.run(['rm', 'john/run/john.pot'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['rm', 'hashcat/hashcat.potfile'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Initialising parser for CLI parsing
    parser = argparse.ArgumentParser(description="Benchmarking hashcat vs JohnTheRipper")
    # usage=usage(), add_help=False)#might wanna write own help

    # Adding arguments to the parser
    parser.add_argument('hash', action='store', choices=['md5', 'sha1', 'sha-256', 'sha-512', 'md5crypt'],
                        help="The hash type to perform a benchmark on.")
    # Parsing for path to supplied hash file, defaults
    parser.add_argument('mode', type=str, choices=['bruteforce', 'bf', 'wordlist', 'wl', 'markov'],
                        help="The mode to perform the benchmark on.")
    parser.add_argument('-file', '-f', help="Path to a file containing hash(es)")
    # Parsing for path to supplied rule file, TODO:currently only supports one for each tool
    parser.add_argument('-rules', '-r', nargs=2,
                        help="Path to rule file to be used by hashcat as well as name of rules to be used by John",
                        metavar="RULE")
    # Parsing for maximum execution time
    parser.add_argument('-time', '-t', type=int, help="Maximum execution time in minutes")
    # Parsing for minimal password length
    parser.add_argument('-minlen', type=int, help="Minimal password length")
    # Parsing for maximum password length
    parser.add_argument('-maxlen', type=int, help="Maximum password length")
    # Parsing for supplied wordlist file
    parser.add_argument('-wordlistfile', '-wlf', help="Path to wordlist file", metavar="FILE")
    # Parsing for flag to disable hashcats markov chains in bruteforce mode
    parser.add_argument('-disablemarkov', action='store_true',
                        help="Flag to disable hashcats markov chains in bruteforce mode")

    args = parser.parse_args()

    # Calling the utility which maps the input hash to the input needed for the tools
    hashes = arg_changer(args.hash)

    # Calling the utility to bring the specified rules into order (john, hashcat)
    rules = order_rules(args.rules)

    # If a maximum execution time was specified in the CLI we convert it from the input minutes to seconds,
    # we do so by multiplying by 30 as each tool only runs for half of the specified time.
    if args.time is not None:
        args.time = args.time * 30

    # Getting file path or trying to default
    if args.file:
        hash_file = args.file
    else:
        try:
            hash_file = get_default_file(args.hash)
        except Exception as e:
            print(e)
            quit()

    # Default password lengths to check, setting values to the specified ones, if supplied
    minlen = 4
    maxlen = 12
    if args.minlen:
        minlen = args.minlen
    if args.maxlen:
        maxlen = args.maxlen

    # Class objects of hashcat and john
    cat = Hashcat()
    jtr = John()

    # Calling the brute force methods and printing the tools speeds
    if args.mode == 'bruteforce' or args.mode == 'bf':

        print("\nRunning brute force benchmark on %s for %d minutes.\n" % (args.hash, args.time/30))

        john_start = time.time()
        john = jtr.bruteforce(hashes[0], minlen, maxlen, hash_file, args.time)
        john_time = time.time() - john_start
        hashcat_start = time.time()
        hashcat = cat.bruteforce(hashes[1], minlen, maxlen, hash_file, args.time, args.disablemarkov)
        hashcat_time = time.time() - hashcat_start

        # Printin results and comparing
        compare(john, hashcat, john_time, hashcat_time, args.time)

    # Calling the wordlist methods and printing the tools speeds
    if args.mode == 'wordlist' or args.mode == 'wl':
        # Checking whether a wordlist has been specified
        if args.wordlistfile is None:
            parser.error("You need to specify a wordlist when benchmarking in wordlist mode!")

        print("\nBenchmarking in wordlist mode on %s for %d minutes.\n" % (args.hash, args.time/30))

        john_start = time.time()
        john = jtr.wordlist(hashes[0], hash_file, args.wordlistfile, rules[0], args.time)
        john_time = time.time() - john_start
        hashcat_start = time.time()
        hashcat = cat.wordlist(hashes[1], hash_file, args.wordlistfile, rules[1], args.time)
        hashcat_time = time.time() - hashcat_start

        # Printin results and comparing
        compare(john, hashcat, john_time, hashcat_time, args.time)

    # Calling the markov mode of john and printing it's speed
    if args.mode == 'markov':

        print("\nBenchmarking with John's markov mode on %s for %d minutes.\n" % (args.hash, args.time/30))

        john_start = time.time()
        john = jtr.markov(hashes[0], hash_file, args.time)
        john_time = time.time() - john_start

        print_results("John", john, john_time, args.time)


# Executing
main()
