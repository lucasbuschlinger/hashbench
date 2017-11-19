import subprocess
import time
import threading
import queue
from utils import *

# Function to capture and filter hashcats output
# TODO: filter correctly if multiple Devices are used
# Required inputs:
#   process:    the process to read from            process
#   speeds:     the list to store the output in     list (mutable)
def hashcat_out(process, speeds=[]):
    # Running while process is still running
    while(process.poll() == None):
        # Read as long as there is data in stdout
        # TODO: could be done nicer?
        while True:
            line = process.stdout.readline()
            if line != '':
                # Filter for speed
                if(line.startswith("Speed")):
                    list_of_string = line.split()
                    # TODO: might not need a loop as we know at which position the desired value is
                    for i in range(0, len(list_of_string)):
                        if(is_float(list_of_string[i])):
                            value = unit_converter(list_of_string[i]+list_of_string[i+1][:-3])
                            speeds.append(value)
                            break
            else:
                break

    # Returning the mutated list containing the recorded values
    return speeds


# Method to perform a wordlist attack with hashcat
# Required inputs:
#   hash:           type of hash                        integer
#   hash_file:      file containing the hash/hashes     string(path)
#   wordlist:       file containing the wordlist        string(path)
#   rules:          the rules to be applied             string(path)
#   max_exec_time:  the maximum time to execute         integer
def hashcat_wordlist(hash, hash_file, wordlist, rules, max_exec_time):

    # Setting a flag whether a maximum execution time was specified
    if(max_exec_time is None):
        no_time = True
    else:
        no_time = False


    if rules == None:
        # Spawn subprocess running an instance of hashcat without rules
        process = subprocess.Popen(["./hashcat/hashcat", "-a0", "-m", "{}".format(hash), hash_file, wordlist, "--status", "--status-timer", "1"],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    else:
        # Spawn subprocess running an instance of hashcat with rules
        process = subprocess.Popen(["./hashcat/hashcat", "-a0", "-m", "{}".format(hash), hash_file, wordlist, "--status", "--status-timer", "1", "-r", rules],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # List to store the collected speeds
    speeds = []

    # Queue to communicate with the timeout thread, enables us to end it, if the process ends prior to timeout
    com_queue = queue.Queue(maxsize=1)

    # This thread captures the output from hashcat
    thread_output = threading.Thread(target=hashcat_out, args=(process, speeds))
    thread_output.start()
    # This thread keeps a look on the time(out)
    thread_timeout = threading.Thread(target=time_watcher, args=(max_exec_time, com_queue))
    thread_timeout.start()

    # While both treads are running OR, if no maximum execution time was specified, while hashcat is running we do absolutely nothing (wasting cycles... IS THERE A BETTER WAY?)
    while(threading.active_count() == 3 or (no_time and (threading.active_count() == 2))):
        pass

    # Terminating hashcat if timeout is reached
    if(thread_output.is_alive()):
        process.terminate()
    thread_output.join()

    # Terminating timeout thread if hashcat is done earlier
    if(thread_timeout.is_alive()):
        com_queue.put("Exit")
    thread_timeout.join()

    # Return average speed
    return sum(speeds)/len(speeds)


# Method to brute force hashes with hashcat
# Required inputs:
#   hash:           type of hash                             integer
#   min:            minimal password length to be tested     integer
#   max:            maximum password length to be tested     integer
#   hash_file:      file containing the hash/hashes          string(path)
#   max_exec_time:  the maximum time to execute              integer
def hashcat_bruteforce(hash, min, max, hash_file, max_exec_time):

    # Setting a flag whether a maximum execution time was specified
    if(max_exec_time is None):
        no_time = True
    else:
        no_time = False

    # Spawn subprocess running an instance of hashcat
    process = subprocess.Popen(["./hashcat/hashcat", "-m", "{}".format(hash), "-a3", "--increment", "--increment-min", "{}".format(min), "--increment-max", "{}".format(max), hash_file ,"?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a", "--status", "--status-timer", "1", "-w", "3", "-O"],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # List to store the collected speeds
    speeds = []

    # Queue to communicate with the timeout thread, enables us to end it, if the process ends prior to timeout
    com_queue = queue.Queue(maxsize=1)

    # This thread captures the output from hashcat
    thread_output = threading.Thread(target=hashcat_out, args=(process, speeds))
    thread_output.start()
    # This thread keeps a look on the time(out)
    thread_timeout = threading.Thread(target=time_watcher, args=(max_exec_time, com_queue))
    thread_timeout.start()

    # While both treads are running OR, if no maximum execution time was specified, while hashcat is running we do absolutely nothing (wasting cycles... IS THERE A BETTER WAY?)
    while(threading.active_count() == 3 or (no_time and (threading.active_count() == 2))):
        pass

    # Terminating hashcat if timeout is reached
    if(thread_output.is_alive()):
        process.terminate()
    thread_output.join()

    # Terminating timeout thread if hashcat is done earlier
    if(thread_timeout.is_alive()):
        com_queue.put("Exit")
    thread_timeout.join()

    # Return average speed
    return sum(speeds)/len(speeds)
