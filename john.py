import subprocess
import time
import threading
import queue
from utils import *

def john_out(process, speeds=[]):
    while(process.poll() == None):
        #Read as long as there is data in stdout
        while True:
            line = process.stdout.readline()
            if line != '':
                list_of_string = line.split()
                for str in list_of_string:
                    #Filter for the speed, given in crypts/sec
                    if(str.endswith("c/s")):
                        value = str[:-3]
                        #Converting speed to MH/s
                        value = unit_converter(value)
                        if(value == 0):
                            break
                        speeds.append(float(value))
                        break
            else:
                break

    return speeds


#Method to perform a wordlist attack with John
#Required inputs:
#   hash: type of hash, string
#   hash_file: file containing the hash/hashes
#   wordlist: file containing the wordlist
#   rules: the rules to be applied
def john_wordlist(hash, hash_file, wordlist, rules, max_exec_time):

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

    com_queue = queue.Queue()

    thread_output = threading.Thread(target=john_out, args=(process, speeds))
    thread_output.start()
    thread_timeout = threading.Thread(target=time_watcher, args=(max_exec_time, com_queue))
    thread_timeout.start()

    while(threading.active_count() == 3 or (no_time and (threading.active_count() == 2))):
        pass

    if(thread_output.is_alive()):
        process.terminate()

    thread_output.join()

    if(thread_timeout.is_alive()):
        com_queue.put("Exit")

    thread_timeout.join()

    return sum(speeds)/len(speeds)

#Method to brute force hashes with john
#Required inputs:
#   hash: type of hash, string
#   min: minimal password length to be tested, integer
#   max: maximum password length to be tested, integer
#   hash_file: file containing the hash/hashes
def john_bruteforce(hash, min, max, hash_file, max_exec_time):

    if(max_exec_time is None):
        no_time = True
    else:
        no_time = False

    #Spawn subprocess running an instance of john
    process = subprocess.Popen(["./john/run/john", "--mask=?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a", "-min-len={}".format(min), "-max-len={}".format(max), hash_file, "--format={}".format(hash), "--verbosity=1", "--progress-every=1"], universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    #List to store the collected speeds
    speeds = []

    com_queue = queue.Queue()

    thread_output = threading.Thread(target=john_out, args=(process, speeds))
    thread_output.start()
    thread_timeout = threading.Thread(target=time_watcher, args=(max_exec_time, com_queue))
    thread_timeout.start()

    while(threading.active_count() == 3 or (no_time and (threading.active_count() == 2))):
        pass

    if(thread_output.is_alive()):
        process.terminate()

    thread_output.join()

    if(thread_timeout.is_alive()):
        com_queue.put("Exit")

    thread_timeout.join()

    #Return average speed
    return sum(speeds)/len(speeds)
