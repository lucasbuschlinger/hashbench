import subprocess
import time
import threading
import queue
from utils import *

# Functio to capture and filter johns output
# Required inputs:
#   process:    the process to read from:           process
#   speeds:     the list to store the output in     list (mutable)
def john_out(process, speeds=[]):
    # Running while process is still running
    while(process.poll() == None):
        first = True
        # Read as long as there is data in stdout
        # TODO: could be done nicer?
        while True:
            line = process.stdout.readline()
            if line != '':
                list_of_string = line.split()
                for str in list_of_string:
                    # Filter for the speed, given in crypts/sec
                    if(str.endswith("c/s")):
                        value = str[:-3]
                        # Converting speed to MH/s
                        value = unit_converter(value)
                        # Skipping first output as it is always 0
                        if(first):
                            first = False
                            break
                        speeds.append(float(value))
                        break
            else:
                break

    # Returning the mutated list containing the recorded values
    return speeds


# Method to perform a wordlist attack with John
# Required inputs:
#   hash: type of hash                          string
#   hash_file: file containing the hash/hashes  string(path)
#   wordlist: file containing the wordlist      string(path)
#   rules: the rules to be applied              string(path)
#   max_exec_time: the maximum time to execute  integer
def john_wordlist(hash, hash_file, wordlist, rules, max_exec_time):

    # Setting a flag whether a maximum execution time was specified
    if(max_exec_time is None):
        no_time = True
    else:
        no_time = False


    if rules == None:
        #Spawn subprocess running an instance of john without rules
        process = subprocess.Popen(["./john/run/john", "--wordlist={}".format(wordlist), hash_file, "--format={}".format(hash), "--verbosity=1", "--progress-every=1"], universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        #Spawn subprocess running an instance of john with rules
        process = subprocess.Popen(["./john/run/john", "--wordlist={}".format(wordlist), hash_file, "--format={}".format(hash), "--verbosity=1", "--progress-every=1", "--rules:{}".format(rules)], universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    #List to store the collected speeds
    speeds = []

    # Queue to communicate with the timeout thread, enables us to end it, if the process ends prior to timeout
    com_queue = queue.Queue(maxsize=1)

    # This thread captures the output from john
    thread_output = threading.Thread(target=john_out, args=(process, speeds))
    thread_output.start()
    # This thread keeps a look on the time(out)
    thread_timeout = threading.Thread(target=time_watcher, args=(max_exec_time, com_queue))
    thread_timeout.start()

    # While both treads are running OR, if no maximum execution time was specified, while hashcat is running we do absolutely nothing (wasting cycles... IS THERE A BETTER WAY?)
    while(threading.active_count() == 3 or (no_time and (threading.active_count() == 2))):
        pass

    # Terminating john if timeout is reached
    if(thread_output.is_alive()):
        process.terminate()
    thread_output.join()

    # Terminating timeout thread if john is done earlier
    if(thread_timeout.is_alive()):
        com_queue.put("Exit")
    thread_timeout.join()

    #Return the average speed
    return sum(speeds)/len(speeds)


# Method to brute force hashes with john
# Required inputs:
#   hash: type of hash                          string
#   min: minimal password length to be tested   integer
#   max: maximum password length to be tested   integer
#   hash_file: file containing the hash/hashes  string(path)
#   max_exec_time: maximum time to execute      integer
def john_bruteforce(hash, min, max, hash_file, max_exec_time):

    # Setting a flag whether a maximum execution time was specified
    if(max_exec_time is None):
        no_time = True
    else:
        no_time = False

    #Spawn subprocess running an instance of john
    process = subprocess.Popen(["./john/run/john", "--mask=?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a", "-min-len={}".format(min), "-max-len={}".format(max), hash_file, "--format={}".format(hash), "--verbosity=1", "--progress-every=1"], universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    #List to store the collected speeds
    speeds = []

    # Queue to communicate with the timeout thread, enables us to end it, if the process ends prior to timeout
    com_queue = queue.Queue(maxsize=1)

    # This thread capture the output from john
    thread_output = threading.Thread(target=john_out, args=(process, speeds))
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

    #Return average speed
    return sum(speeds)/len(speeds)
