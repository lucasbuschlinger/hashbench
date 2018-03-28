from .utils import *


def print_results(tool, results, run_times, time_spec, individual_stats, runs):
    """Prints the results and statistics to the command line

        Arguments:
            tool                (string):   hashcat or john
            results             (list):     tool's collected output
            run_times           (list):     duration of runs
            time_spec           (int):      maximum execution time
            individual_stats    (bool):     flag to print stats for individual runs
            runs                (int):      number of runs

        Returns:
            median_speed    (float):    average speed of tool for comparison
            avg_cracked     (int):      average number of cracked hashes for comparison
    """

    if len(run_times) == 0 or len(results[0]) == 0 or len(results[1]) == 0 or len(results[2]) == 0:
        print("No sufficient data for %s => no statistics displayed" % tool)
        return -1, -1

    avg_duplicates = int(sum(results[3])/len(results[3]))
    avg_cracked = int(sum(results[0])/len(results[0])) - avg_duplicates
    avg_detected = int(sum(results[1])/len(results[1]))
    avg_time_run = float(sum(run_times)/len(run_times))
    hashes_per_sec = int(avg_cracked / avg_time_run)
    temp = concat_speedlists(results[2], results[4])
    all_speeds = temp[0]
    all_speeds_trimmed = trim(all_speeds, 0.05)
    avg_removed = statistics.mean(temp[1])
    mean_speed = statistics.mean(all_speeds)
    standard_deviation = statistics.stdev(all_speeds)
    trimmed_mean_speed = statistics.mean(all_speeds_trimmed)
    standard_deviation_trimmed = statistics.stdev(all_speeds_trimmed)
    median_speed = statistics.median(all_speeds)
    interquartile_range = quartiles_range(all_speeds)

    print("Average results for %s over all runs:" % tool)
    print("  Mean speed: %.3f MH/s (Spread: %.3f MH/s (standard deviation))" % (mean_speed, standard_deviation))
    print("  Trimmed mean speed (trim: 5%%): %.3f MH/s (Spread: %.3f MH/s (standard deviation))"
          % (trimmed_mean_speed, standard_deviation_trimmed))
    print("  Median speed: %.3f MH/s (Spread: %.3f MH/s (interquartile range))" % (median_speed, interquartile_range))
    print("  Average cracked hashes per run: %d/%d" % (avg_cracked, avg_detected))
    if avg_duplicates > 0:
        print("  On average %d additional, duplicate hashes were cracked" % avg_duplicates)
    print("  Average time per run: %.3fs" % avg_time_run)
    print("  Number of cracked hashes per second (per run): %d" % hashes_per_sec)
    print("  On average the speeds of the first %d seconds were ignored (getting up to speed)" % int(avg_removed))

    if avg_cracked == avg_detected:
        print("  %s finished early, managed to crack all %d hashes!" % (tool, avg_detected))
    elif time_spec is not None:
        if avg_time_run < time_spec:
            print("  %s finished early! => Keyspace exhausted or all hashes cracked!" % tool)

    if individual_stats and runs > 1:
        print("\n  Individual stats:")
        for i in range(runs):
            cracked = int(results[0][i])
            detected = int(results[1][i])
            time_run = run_times[i]
            hashes_per_sec = int(cracked / time_run)
            removed = remove_startup(results[2][i])
            mean_speed = statistics.mean(results[2][i])
            median_speed = statistics.median(results[2][i])
            trimmed_speeds = trim(results[2][i], 0.05)
            trimmed_mean_speed = statistics.mean(trimmed_speeds)
            if (len(results[2][i])) > 1:
                standard_deviation = statistics.stdev(results[2][i])
            else:
                standard_deviation = 0
            if len(trimmed_speeds) > 1:
                standard_deviation_trimmed = statistics.stdev(trimmed_speeds)
            else:
                standard_deviation_trimmed = 0
            interquartile_range = quartiles_range(results[2][i])
            print("    Statistics for %s's %d. run:" % (tool, i+1))
            print("      Mean speed: %.3f MH/s (Spread: %.3f MH/s (standard deviation))"
                  % (mean_speed, standard_deviation))
            print("      Trimmed mean speed (trim: 5%%): %.3f MH/s (Spread: %.3f MH/s (standard deviation))"
                  % (trimmed_mean_speed, standard_deviation_trimmed))
            print("      Median speed: %.3f MH/s (Spread: %.3f MH/s (interquartile range))"
                  % (median_speed, interquartile_range))
            print("      Cracked hashes: %d/%d" % (cracked, detected))
            print("      Time run: %.3fs" % time_run)
            print("      Number of cracked hashes per second: %d" % hashes_per_sec)
            print("      The speeds of the first %d seconds were ignored (getting up to speed)" % removed)

    return median_speed, avg_cracked


# Helper to compare the tools
def compare(john_results, hashcat_results, john_time, hashcat_time, time_spec, individual_stats, runs):
    """Compares results and prints statistics

        Arguments:
            john_results        (list): collected values of john
            hashcat_results     (list): collected values of hashcat
            john_time           (list): run durations of john
            hashcat_time        (list): run durations of hashcat
            time_spec           (int):  maximum execution time
            individual_stats    (bool): flag to print individual stats
            runs                (int):  number of runs run
    """

    john = print_results("John", john_results, john_time, time_spec, individual_stats, runs)

    print("\n")

    hashcat = print_results("Hashcat", hashcat_results, hashcat_time, time_spec, individual_stats, runs)

    speed_comparison = hashcat[0]/john[0]
    cracked_comparison = hashcat[1]/john[1]

    if hashcat[0] != -1 and john[0] != -1:
        print("\nIn comparison:")
        if speed_comparison >= 1:
            print("  Speed-wise Hashcat was %.3fx faster as John" % speed_comparison)
        else:
            print("  Speed-wise Hashcat was only %.3fx as fast as John" % speed_comparison)

        print("  On average Hashcat cracked %.3fx as many hashes as John" % cracked_comparison)
    else:
        pass
