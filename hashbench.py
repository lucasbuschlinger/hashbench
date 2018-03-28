from modules.hasher import *
from modules.hashcat import *
from modules.john import *
from modules.output import *
from modules.plot import *
from modules.utils import *

from copy import deepcopy
from operator import sub
import argparse
import os
import time


def main():
    """Main function, parses command line, calls runners and output functions."""

    # Initialising parser for CLI parsing
    parser = argparse.ArgumentParser(description="Benchmarking hashcat vs JohnTheRipper")
    # usage=usage(), add_help=False)#might wanna write own help

    # Adding arguments to the parser
    parser.add_argument('hash', action='store', choices=['md4', 'md5', 'sha1', 'sha-256', 'sha-512', 'md5crypt'],
                        help="The hash type to perform a benchmark on.")
    # Parsing for path to supplied hash file, defaults
    parser.add_argument('mode', type=str, choices=['bruteforce', 'bf', 'wordlist', 'wl'],
                        help="The mode to perform the benchmark on.")
    parser.add_argument('-file', '-f', help="Path to a file containing hash(es)")
    # Parsing for path to supplied rule file
    parser.add_argument('-rules', '-r', nargs=2,
                        help="Path to rule file to be used by hashcat as well as name of rules to be used by John",
                        metavar="RULE")
    # Parsing for maximum execution time
    parser.add_argument('-time', '-t', type=int, help="Maximum execution time in minutes")
    # Parsing for minimal password length
    parser.add_argument('-minlen', type=int, default=4, help="Minimal password length")
    # Parsing for maximum password length
    parser.add_argument('-maxlen', type=int, default=15, help="Maximum password length")
    # Parsing for supplied wordlist file
    parser.add_argument('-wordlistfile', '-wlf', help="Path to wordlist file", metavar="FILE")
    # Parsing for flag to disable hashcats markov chains in bruteforce mode
    parser.add_argument('-disablemarkov', action='store_true',
                        help="Flag to disable hashcats markov chains in bruteforce mode")
    # Paring for how many runs should be commenced.
    parser.add_argument('-multirun', type=int, default=1, help="Number of runs each tool should perform")
    # Parsing for flag to print results for the individual runs
    parser.add_argument('-individualstats', action='store_true',
                        help="Flag to print out individual stats per run"
                             " (only takes effect when more than 1 run is performed)")
    parser.add_argument('-generate', '-g', nargs=2, help="Generates N hashes from the supplied file every run",
                        metavar=("N", "FILE"))
    parser.add_argument('-graphic', action='store_true', help="Flag to generate plots")

    args = parser.parse_args()
    try:
        config = load_config()
    except ValueError as error:
        print(str(error) + ". Exiting...")
        exit(1)

    john_loc = config["HASHBENCH"]["location_john"]
    hashcat_loc = config["HASHBENCH"]["location_hashcat"]

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

    else:
        print("\nWARNING: No time limit specified, might not terminate in reasonable time!")

    # Getting file path or trying to default
    if args.file:
        hash_file = args.file
    else:
        try:
            hash_file = get_default_file(args.hash)
        except Exception as e:
            print(e)
            quit()

    # Class objects of hashcat and john
    hashcat = Hashcat()
    john = John()

    # List for storing john's output
    john_out = [], [], [], [], []
    # List for storing hashcat's output
    hashcat_out = [], [], [], [], []

    john_times = []
    hashcat_times = []

    if args.mode == "bf" or args.mode == "bruteforce":
        args.mode = "brute force"
        mode = 1
    elif args.mode == "wl" or args.mode == "wordlist":
        if not args.wordlistfile:
            print("A wordlist is required in dictionary mode! Exiting...")
            exit(1)
        args.mode = "wordlist"
        mode = 0

    if args.time is not None:
        print("\nRunning {} benchmark on {}, running each tool {}x {}sec for a total of {}min.\n".format(
            args.mode, args.hash, args.multirun, args.time, runtime))
    else:
        print("\nRunning {} benchmark on {}, running {}x.\n".format(args.mode, args.hash, args.multirun))

    try:

        for run in range(args.multirun):
            # Removing potfiles to have maximum work to do
            try:
                os.remove(john_loc + '.pot')
            except FileNotFoundError:
                # If FileNotFoundError occurs we do not have to delete it
                pass
            try:
                os.remove(hashcat_loc + '.potfile')
            except FileNotFoundError:
                # If FileNotFoundError occurs we do not have to delete it
                pass

            if args.generate is not None:
                try:
                    generate_hashes(args.generate[1], int(args.generate[0]), args.hash)
                except ValueError:
                    print("Could not generate hashes for %s, exiting..." % args.hash)
                    exit(1)
                hash_file = "gen.hash"

            john_start = time.time()
            john_tmpout = john.execute(john_loc, mode, hashes[0], hash_file, args.time, args.wordlistfile, rules[0],
                                       args.minlen, args.maxlen)
            john_end = time.time() - john_start

            john_out[0].append(john_tmpout[0])
            john_out[1].append(john_tmpout[1])
            john_out[2].append(john_tmpout[2])
            john_out[3].append(duplicate_check(john_loc + ".pot"))
            john_out[4].append(john_tmpout[3])
            john_times.append(john_end)

            hashcat_start = time.time()
            hashcat_tmpout = hashcat.execute(hashcat_loc, mode, hashes[1], hash_file, args.time, args.wordlistfile,
                                             rules[1], args.minlen, args.maxlen, args.disablemarkov)
            hashcat_end = time.time() - hashcat_start

            hashcat_out[0].append(hashcat_tmpout[0])
            hashcat_out[1].append(hashcat_tmpout[1])
            hashcat_out[2].append(hashcat_tmpout[2])
            hashcat_out[3].append(duplicate_check(hashcat_loc + ".potfile"))
            hashcat_out[4].append(hashcat_tmpout[3])
            hashcat_times.append(hashcat_end)

            completion = int(100 * ((run + 1) / args.multirun))
            print("Completed run %d/%d => %d%% done..." % (run + 1, args.multirun, completion), end="\r")

    except KeyboardInterrupt:
        if run == 0:
            print("\rEarly exit due to KeyboardInterrupt. No data to display (0 runs completed)")
            exit(1)
        else:
            print("\rEarly exit due to KeyboardInterrupt => Fewer data available (only %d run(s) completed)\n" % run)

    # Printing results and comparing
    try:
        compare(deepcopy(john_out), deepcopy(hashcat_out), john_times, hashcat_times, args.time, args.individualstats,
                args.multirun)
    except statistics.StatisticsError:
        print("Error while generating statistics, probably did not get data from one of the tools")

    # Generating graphics, if wished
    if args.graphic:
        plot_speeds(john_out[2], hashcat_out[2], john_out[4], hashcat_out[4])
        max_detected = max(map(max, [john_out[1], hashcat_out[1]]))
        john_cracked_unique = list(map(sub, john_out[0], john_out[3]))
        hashcat_cracked_unique = list(map(sub, hashcat_out[0], hashcat_out[3]))
        plot_cracked(john_cracked_unique, hashcat_cracked_unique, max_detected)


# Executing
main()
