import time
import queue
import statistics


# Helper to map the given hash type to the required format by john and hashcat respectively
# noinspection SpellCheckingInspection
def arg_changer(hash_type):
    if hash_type == "md5":
        return "raw-md5-opencl", 0
    elif hash_type == 'md4':
        return "raw-md4-opencl", 900
    elif hash_type == 'sha1':
        return "raw-sha1-opencl", 100
    elif hash_type == 'sha-256':
        return "raw-sha256-opencl", 1400
    elif hash_type == 'sha-512':
        return "raw-sha512-opencl", 1700
    elif hash_type == 'md5crypt':
        return 'md5crypt-opencl', 500


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
def print_results(tool, results, run_times, time_spec, individual_stats, runs):

    avg_cracked = int(sum(results[0])/len(results[0]))
    avg_detected = int(sum(results[1])/len(results[1]))
    avg_time_run = float(sum(run_times)/len(run_times))
    hashes_per_sec = int(avg_cracked / avg_time_run)
    time_remaining = ((avg_detected - avg_cracked) / hashes_per_sec)
    temp = concat_speedlists(results[2])
    all_speeds = temp[0]
    avg_removed = statistics.mean(temp[1])
    mean_speed = statistics.mean(all_speeds)
    standard_variance = statistics.stdev(all_speeds)
    trimmed_mean_speed = statistics.mean(trim(all_speeds, 0.05))
    median_speed = statistics.median(all_speeds)
    interquartile_range = quartiles_range(all_speeds)

    print("Average results for %s over all runs:" % tool)
    print("  Mean speed: %.3f MH/s (Spread: %.3f MH/s (standard variance))" % (mean_speed, standard_variance))
    print("  Trimmed mean speed (trim: 5%%): %.3f MH/s" % trimmed_mean_speed)
    print("  Median speed: %.3f MH/s (Spread: %.3f MH/s (interquartile range))" % (median_speed, interquartile_range))
    print("  Average cracked hashes per run: %d/%d" % (avg_cracked, avg_detected))
    print("  Average time per run: %.3fs" % avg_time_run)
    print("  Number of cracked hashes per second (per run): %d" % hashes_per_sec)
    print("  On average the speeds of the first %d seconds were ignored (getting up to speed)" % int(avg_removed))

    if individual_stats:
        print("\n  Individual stats:")
        for i in range(runs):
            cracked = int(results[0][i])
            detected = int(results[1][i])
            temp = remove_startup(results[2][i])
            speeds = temp[0]
            removed = temp[1]
            time_run = run_times[i]
            mean_speed = statistics.mean(speeds)
            median_speed = statistics.median(speeds)
            trimmed_mean_speed = statistics.mean(trim(speeds, 0.05))
            print("    Statistics for %s's %d. run:" % (tool, i+1))
            print("      Mean speed: %.3f MH/s" % mean_speed)
            print("      Trimmed mean speed (trim: 5%%): %.3f MH/s" % trimmed_mean_speed)
            print("      Median speed: %.3f MH/s" % median_speed)
            print("      Cracked hashes: %d/%d" % (cracked, detected))
            print("      Time run: %.3fs" % time_run)
            print("      Number of cracked hashes per second: %d" % int(cracked/time_run))
            print("      The speeds of the first %d seconds were ignored (getting up to speed)" % removed)

    if avg_cracked == avg_detected:
        print("  %s finished early, managed to crack all %d hashes!" % (tool, avg_detected))
    #elif time_spec is not None:
     #   if time_run < time_spec:
      #      print("  %s finished early! => Keyspace exhausted!" % tool)
        #else:
        #    print("  Theoretical time to crack remaining hashes (using average cracking rate, probably incorrect):"
        #          " %.3fs"
        #          % time_remaining)

    return trimmed_mean_speed, avg_cracked


# Helper to compare the tools
def compare(john_results, hashcat_results, john_time, hashcat_time, time_spec, individual_stats, runs):

    john = print_results("John", john_results, john_time, time_spec, individual_stats, runs)

    print("\n")

    hashcat = print_results("Hashcat", hashcat_results, hashcat_time, time_spec, individual_stats, runs)

    speed_comparison = hashcat[0]/john[0]
    cracked_comparison = hashcat[1]/john[1]

    print("\nIn comparison:")
    if speed_comparison >= 1:
        print("  Speed-wise Hashcat was %.3fx faster as John" % speed_comparison)
    else:
        print("  Speed-wise Hashcat was only %.3fx as fast as John" % speed_comparison)

    print("  On average Hashcat cracked %.3fx as many hashes as John" % cracked_comparison)


# Helper to trim outliers from the speed list
def trim(speeds, trim_percentage):
    trim_amount = int(len(speeds)*trim_percentage)
    tmpspeeds = sorted(speeds)
    if trim_amount > 1:
        for i in range(0, trim_amount, 2):
            tmpspeeds.pop(0)
            tmpspeeds.pop()
    return tmpspeeds


# Helper to concatenate the lists of speeds produced by the multiple runs
# Simultaneously removes the first x values where the tools get up to speed
def concat_speedlists(inputlist):
    tmplist = []
    removed = []
    for i in range(len(inputlist)):
        removed.append(remove_startup(inputlist[i]))
        tmplist += inputlist[i]
    return tmplist, removed


# Helper to remove the slow speeds caused by startup
def remove_startup(speeds=[]):
    i = 0
    for i in range(len(speeds)-1):
        mean_after = statistics.median(speeds[i+1:])
        if speeds[i] > mean_after * 0.99:
            break

    for j in range(i):
        speeds.pop(0)

    return i


# Helper to get lower and upper quartiles of the data supplied
def quartiles_range(values):
    tmpvalues = sorted(values)
    entries = len(tmpvalues)
    if entries % 2 == 0:
        lower = int(entries * 0.25)
        upper = int(entries * 0.75)
    else:
        lower = int(entries * 0.25) + 1
        upper = int(entries * 0.75) + 1
        
    return tmpvalues[upper] - tmpvalues[lower]
