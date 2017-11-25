import subprocess
import time
import threading
import queue
from utils import *


# Function to capture and filter johns output
# Required inputs:
#   process:    the process to read from:           process
#   speeds:     the list to store the output in     list (mutable)
# Returns:
#   mutated list 'speeds' containing (number of cracked hashes, (speed)*)
# noinspection PyDefaultArgument
def john_out(process, ignore, speeds=[]):
    # Running while process is still running
    count = 0
    while process.poll() is None:
        # Read as long as there is data in stdout
        while True:
            line = process.stdout.readline()
            # Skipping the first 3 or 4 lines as they are not relevant
            if count < ignore:
                # Getting how many hashes there are detected in the input file
                if count == 1:
                    speeds[1] = int(line.split()[1])

                count += 1
                break

            if line != '':
                list_of_string = line.split()
                # Checking the first element as this indicates whether we have a valid line
                first_elem = list_of_string[0][:-1]
                if is_float(first_elem):
                    # Setting first list element to the number of cracked hashes
                    speeds[0] = int(first_elem)
                    # Appending current speed to list
                    if list_of_string[2] == 'DONE':
                        speed = list_of_string[6][:-3]
                    else:
                        speed = list_of_string[7][:-3]
                    speed = unit_converter(speed)
                    speeds.append(float(speed))

            else:
                break

    # Returning the mutated list containing the recorded values
    return speeds


# Method to perform a wordlist attack with John
# Required inputs:
#   hash_type: type of hash                     string
#   hash_file: file containing the hash/hashes  string(path)
#   wordlist: file containing the wordlist      string(path)
#   rules: the rules to be applied              string(path)
#   max_exec_time: the maximum time to execute  integer
# Returns:
#   list containing (number of cracked hashes, average speed)
def john_wordlist(hash_type, hash_file, wordlist, rules, max_exec_time):

    # Setting a flag whether a maximum execution time was specified
    if max_exec_time is None:
        no_time = True
    else:
        no_time = False

    if rules is None:
        # Spawn subprocess running an instance of john without rules
        process = subprocess.Popen(["./john/run/john", "--wordlist={}".format(wordlist), hash_file,
                                    "--format={}".format(hash_type), "--verbosity=1", "--progress-every=1"],
                                   universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    else:
        # Spawn subprocess running an instance of john with rules
        process = subprocess.Popen(["./john/run/john", "--wordlist={}".format(wordlist), hash_file,
                                    "--format={}".format(hash_type), "--verbosity=1", "--progress-every=1",
                                    "--rules:{}".format(rules)], universal_newlines=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # List to store number of cracked hashes and speeds
    speeds = [0, 0]

    # Queue to communicate with the timeout thread, enables us to end it, if the process ends prior to timeout
    com_queue = queue.Queue(maxsize=1)

    # This thread captures the output from john
    thread_output = threading.Thread(target=john_out, args=(process, 4, speeds))
    thread_output.start()
    # This thread keeps a look on the time(out)
    thread_timeout = threading.Thread(target=time_watcher, args=(max_exec_time, com_queue))
    thread_timeout.start()

    # While both treads are running OR, if no maximum execution time was specified, we stall this process
    while threading.active_count() == 3 or (no_time and (threading.active_count() == 2)):
        time.sleep(1)

    # Terminating john if timeout is reached
    if thread_output.is_alive():
        process.terminate()
    thread_output.join()

    # Terminating timeout thread if john is done earlier
    if thread_timeout.is_alive():
        com_queue.put("Exit")
    thread_timeout.join()

    # Returning a tuple containing (#cracked hashes, #detected, hashes, average speed)
    return speeds.pop(0), speeds.pop(0), sum(speeds) / len(speeds)


# Method to brute force hashes with john
# Required inputs:
#   hash_type: type of hash                     string
#   min: minimal password length to be tested   integer
#   max: maximum password length to be tested   integer
#   hash_file: file containing the hash/hashes  string(path)
#   max_exec_time: maximum time to execute      integer
# Returns:
#   list containing (number of cracked hashes, average speed)
def john_bruteforce(hash_type, min_length, max_length, hash_file, max_exec_time):

    # Setting a flag whether a maximum execution time was specified
    if max_exec_time is None:
        no_time = True
    else:
        no_time = False
    # Spawn subprocess running an instance of john
    process = subprocess.Popen(["./john/run/john", "--mask=?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a",
                                "-min-len={}".format(min_length), "-max-len={}".format(max_length), hash_file,
                                "--format={}".format(hash_type), "--verbosity=1", "--progress-every=1"],
                               universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    time_start = time.time()

    # List to store number of cracked hashes and speeds
    speeds = [0, 0]

    # Queue to communicate with the timeout thread, enables us to end it, if the process ends prior to timeout
    com_queue = queue.Queue(maxsize=1)

    # This thread capture the output from john
    thread_output = threading.Thread(target=john_out, args=(process, 4, speeds))
    thread_output.start()
    # This thread keeps a look on the time(out)
    thread_timeout = threading.Thread(target=time_watcher, args=(max_exec_time, com_queue))
    thread_timeout.start()

    # While both treads are running OR, if no maximum execution time was specified, we stall this process
    while threading.active_count() == 3 or (no_time and (threading.active_count() == 2)):
        time.sleep(1)

    # Terminating hashcat if timeout is reached
    if thread_output.is_alive():
        process.terminate()
    print(time.time()-time_start)
    thread_output.join()

    # Terminating timeout thread if hashcat is done earlier
    if thread_timeout.is_alive():
        com_queue.put("Exit")
    thread_timeout.join()

    # Returning a tuple containing (#cracked hashes, #detected, hashes, average speed)
    return speeds.pop(0), speeds.pop(0), sum(speeds) / len(speeds)
