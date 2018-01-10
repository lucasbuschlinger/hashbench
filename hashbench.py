import argparse
from modules.utils import *
from modules.hashcat import *
from modules.john import *
import os


# noinspection SpellCheckingInspection
def main():

    # Initialising parser for CLI parsing
    parser = argparse.ArgumentParser(description="Benchmarking hashcat vs JohnTheRipper")
    # usage=usage(), add_help=False)#might wanna write own help

    # Adding arguments to the parser
    parser.add_argument('hash', action='store', choices=['md4', 'md5', 'sha1', 'sha-256', 'sha-512', 'md5crypt'],
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
    # Parsing for flag to use --mask on john's wordlist mode
    parser.add_argument('-enablemask', action='store_true',
                        help="Flag to enable --mask option on john's wordlist mode")
    # Paring for how many runs should be commenced.
    parser.add_argument('-multirun', type=int, default=1, help="Number of runs each tool should perform")
    # Parsing for flag to print results for the individual runs
    parser.add_argument('-individualstats', action='store_true',
                        help="Flag to print out individual stats per run"
                             " (only takes effect when more than 1 run is performed)")

    args = parser.parse_args()

    # Calling the utility which maps the input hash to the input needed for the tools
    hashes = arg_changer(args.hash)

    # Calling the utility to bring the specified rules into order (john, hashcat)
    rules = order_rules(args.rules)

    runtime = args.time
    # If a maximum execution time was specified in the CLI we convert it from the input minutes to seconds,
    # we do so by multiplying by 30 as each tool only runs for half of the specified time.
    if args.time is not None:
        args.time = args.time * 30 / args.multirun

        if args.time <= 15:
            print("\nWARNING: Very short execution time of %dsec per run. Consider longer runtimes" % args.time
                  + " (at least 30sec per run) to avoid slower times due to the tools having to get up to speed!")

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
    hashcat = Hashcat()
    john = John()

    # Calling the brute force methods and printing the tools speeds
    if args.mode == 'bruteforce' or args.mode == 'bf':

        if args.time is not None:
            print("\nRunning brute force benchmark on %s, running each tool %dx %dsec for a total of %dmin.\n"
                  % (args.hash, args.multirun, args.time, runtime))
        else:
            print("\nRunning brute force benchmark on %s, running %d times.\n" % (args.hash, args.multirun))

        # List for storing john's output
        john_out = [], [], []
        # List for storing hashcat's output
        hashcat_out = [], [], []

        john_times = []
        hashcat_times =[]

        try:

            for var in range(args.multirun):

                # Removing potfiles to have maximum work to do
                try:
                    os.remove('john/run/john.pot')
                except FileNotFoundError:
                    # If FileNotFoundError occurs it we do not have to delete it
                    pass
                try:
                    os.remove('hashcat/hashcat.potfile')
                except FileNotFoundError:
                    # If FileNotFoundError occurs it we do not have to delete it
                    pass

                john_start = time.time()
                john_tmpout = john.bruteforce(hashes[0], minlen, maxlen, hash_file, args.time)
                john_end = time.time() - john_start

                john_out[0].append(john_tmpout[0])
                john_out[1].append(john_tmpout[1])
                john_out[2].append(john_tmpout[2])
                john_times.append(john_end)

                hashcat_start = time.time()
                hashcat_tmpout = hashcat.bruteforce(hashes[1], minlen, maxlen, hash_file, args.time, args.disablemarkov)
                hashcat_end = time.time() - hashcat_start

                hashcat_out[0].append(hashcat_tmpout[0])
                hashcat_out[1].append(hashcat_tmpout[1])
                hashcat_out[2].append(hashcat_tmpout[2])
                hashcat_times.append(hashcat_end)

        except KeyboardInterrupt:
            if var == 0:
                print("\rEarly exit due to KeyboardInterrupt. No data to display (0 runs completed)")
                exit(1)
            else:
                print("\rEarly exit due to KeyboardInterrupt => Fewer data available (only %d run(s) completed)\n" % var)

        # Printing results and comparing
        compare(john_out, hashcat_out, john_times, hashcat_times, args.time, args.individualstats, args.multirun)

    # Calling the wordlist methods and printing the tools speeds
    if args.mode == 'wordlist' or args.mode == 'wl':
        # Checking whether a wordlist has been specified
        if args.wordlistfile is None:
            parser.error("You need to specify a wordlist when benchmarking in wordlist mode!")

        if args.time is not None:
            print("\nRunning wordlist benchmark on %s, running each tool %dx %dsec for a total of %dmin.\n"
                  % (args.hash, args.multirun, args.time, runtime))
        else:
            print("\nRunning wordlist benchmark on %s, running %d times.\n" % (args.hash, args.multirun))

        # List for storing john's output
        john_out = [], [], []
        # List for storing hashcat's output
        hashcat_out = [], [], []

        john_times = []
        hashcat_times = []

        for var in range(args.multirun):
            # Removing potfiles to have maximum work to do
            try:
                os.remove('john/run/john.pot')
            except FileNotFoundError:
                # If FileNotFoundError occurs it we do not have to delete it
                pass
            try:
                os.remove('hashcat/hashcat.potfile')
            except FileNotFoundError:
                # If FileNotFoundError occurs it we do not have to delete it
                pass

            john_start = time.time()
            john_tmpout = john.wordlist(hashes[0], hash_file, args.wordlistfile, rules[0], args.enablemask, args.time)
            john_end = time.time() - john_start

            john_out[0].append(john_tmpout[0])
            john_out[1].append(john_tmpout[1])
            john_out[2].append(john_tmpout[2])
            john_times.append(john_end)

            hashcat_start = time.time()
            hashcat_tmpout = hashcat.wordlist(hashes[1], hash_file, args.wordlistfile, rules[1], args.time)
            hashcat_end = time.time() - hashcat_start

            hashcat_out[0].append(hashcat_tmpout[0])
            hashcat_out[1].append(hashcat_tmpout[1])
            hashcat_out[2].append(hashcat_tmpout[2])
            hashcat_times.append(hashcat_end)

        # Printin results and comparing
        compare(john_out, hashcat_out, john_times, hashcat_times, args.time, args.individualstats, args.multirun)

    # Calling the markov mode of john and printing it's speed
    if args.mode == 'markov':

        print("\nBenchmarking with John's markov mode on %s for %d minutes.\n" % (args.hash, args.time/30))

        john_start = time.time()
        john_out = john.markov(hashes[0], hash_file, args.time)
        john_times = time.time() - john_start

        print_results("John", john_out, john_times, args.time)


# Executing
main()
