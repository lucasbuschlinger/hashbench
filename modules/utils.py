import time
import queue


# Helper to map the given hash type to the required format by john and hashcat respectively
# noinspection SpellCheckingInspection
def arg_changer(hash_type):
    hashes = []

    if hash_type == "md5":
        hashes.append("raw-md5-opencl")
        hashes.append(0)
    elif hash_type == 'md4':
        hashes.append("raw-md4-opencl")
        hashes.append(900)
    elif hash_type == 'sha1':
        hashes.append("raw-sha1-opencl")
        hashes.append(100)
    elif hash_type == 'sha-256':
        hashes.append("raw-sha256-opencl")
        hashes.append(1400)
    elif hash_type == 'sha-512':
        hashes.append("raw-sha512-opencl")
        hashes.append(1700)
    elif hash_type == 'md5crypt':
        hashes.append('md5crypt-opencl')
        hashes.append(500)

    return hashes


# Helper to check whether the given string is a float
def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# Helper to convert speed to MH/s
def unit_converter(value):
    if value.endswith("M"):
        return float(value[:-1])
    else:
        if value.endswith("K") or value.endswith("k"):
            return float(value[:-1])/1000
        elif value.endswith("G"):
            return float(value[:-1])*1000
        elif value.isdigit():
            return float(value)/1000/1000
        else:
            # Might want to throw an exception here...
            print("NO VALID TYPE")


# Helper to supply correct default hash file to tools, if given
def get_default_file(hash_type):
    if hash_type == 'md5':
        return "resources/hashes/top10k.md5"
    elif hash_type == 'sha1':
        return "resources/hashes/top10k.sh1"
    elif hash_type == 'sha-256':
        return "resources/hashes/top10k.sha256"
    elif hash_type == 'sha-512':
        return "resources/hashes/top10k.sha512"
    elif hash_type == 'md5crypt':
        return "resources/hashes/top10k.md5crypt"
    else:
        raise Exception('No default file for %s-hashes available! Please supply a file containing hashes!' % hash)


# Printing own help
def usage():
    f = open('doc/usage.txt', 'r')
    file_contents = f.read()
    print(file_contents)
    f.close()


# Watcher for maximum execution time
def time_watcher(max_exec_time, com_queue):
    if max_exec_time is None:
        quit()
    start_time = time.time()
    while True and com_queue.empty():
        time_run = time.time() - start_time
        if time_run > max_exec_time:
            quit()
        time.sleep(1)


# Helper to put specified rules into desired order (john, hashcat)
def order_rules(rules):
    ordered_rules = []
    if rules is None:
        ordered_rules.append(None)
        ordered_rules.append(None)
        return ordered_rules
    elif rules[0].endswith('.rule'):
        ordered_rules.append(rules[1])
        ordered_rules.append(rules[0])
        return ordered_rules
    else:
        return rules


# Helper to print some results
def print_results(tool, results, time_run, time_spec):

    hashes_per_sec = int(results[0] / time_run)
    time_remaining = ((results[1] - results[0]) / (int(results[0] / time_run)))

    print("Results for %s:" % tool)
    print("  Average Speed: %.3f MH/s" % results[2])
    print("  Cracked hashes: %d/%d" % (results[0], results[1]))
    print("  Time run: %.3fs" % time_run)
    print("  Theoretical number of cracked hashes per second: %d" % hashes_per_sec)

    if results[0] == results[1]:
        print("  %s finished early, managed to crack all %d hashes!" % (tool, results[1]))
    elif time_spec is not None:
        if time_run < time_spec:
            print("  %s finished early! => Keyspace exhausted!" % tool)
        else:
            print("  Theoretical time to crack remaining hashes (using average cracking rate, probably incorrect):"
                  " %.3fs"
                  % time_remaining)


# Helper to compare the tools
def compare(john_results, hashcat_results, john_time, hashcat_time, time_spec):

    print_results("John", john_results, john_time, time_spec)

    print("\n")

    print_results("Hashcat", hashcat_results, hashcat_time, time_spec)

    speed_comparison = hashcat_results[2]/john_results[2]
    cracked_comparison = hashcat_results[0]/john_results[0]

    print("\nIn comparison:")
    if speed_comparison >= 1:
        print("  Speed-wise hashcat was %.3fx faster as john" % speed_comparison)
    else:
        print("  Speed-wise hashcat was only %.3fx as fast as john" % speed_comparison)

    print("  Hashcat cracked %.3fx as many hashes as john" % cracked_comparison)