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

def hashcat_out(process, speeds=[]):
    while(process.poll() == None):
        #process.stdin.write("s\n")
        #process.stdin.flush
        #Read as long as there is data in stdout
        while True:
            line = process.stdout.readline()
            if line != '':
                #Filter for speed
                if(line.startswith("Speed")):
                    list_of_string = line.split()
                    for i in range(0, len(list_of_string)):
                        if(is_float(list_of_string[i])):
                            value = unit_converter(list_of_string[i]+list_of_string[i+1][:-3])
                            speeds.append(value)
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

    #Getting output from john while process is running
    #while(process.poll() == None):
    #    #Read as long as there is data in stdout
    #    while True:
    #        line = process.stdout.readline()
    #        if line != '':
    #            list_of_string = line.split()
    #            for str in list_of_string:
    #                #Filter for the speed, given in crypts/sec
    #                if(str.endswith("c/s")):
    #                    value = str[:-3]
    #                    #Converting speed to MH/s
    #                    value = unit_converter(value)
    #                    if(value == 0):
    #                        break
    #                    speeds.append(float(value))
    #                    break
    #        else:
    #            break
    #Return average speed

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

####################################################################################################

#Method to brute force hashes with hashcat
#Required inputs:
#   hash: type of hash, integer
#   hash_file: file containing the hash/hashes
#   wordlist: file containing the wordlist
#   rules: the rules to be applied
def hashcat_wordlist(hash, hash_file, wordlist, rules, max_exec_time):

    if(max_exec_time is None):
        no_time = True
    else:
        no_time = False

    if rules == None:
        #Spawn subprocess running an instance of hashcat without rules
        process = subprocess.Popen(["./hashcat/hashcat", "-a0", "-m", "{}".format(hash), hash_file, wordlist, "--status", "--status-timer", "1"],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    else:
        #Spawn subprocess running an instance of hashcat with rules
        process = subprocess.Popen(["./hashcat/hashcat", "-a0", "-m", "{}".format(hash), hash_file, wordlist, "--status", "--status-timer", "1", "-r", rules],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    #List to store the collected speeds
    speeds = []

#    while(process.poll() == None):
#        #process.stdin.write("s\n")
#        #process.stdin.flush
#        #Read as long as there is data in stdout
#        while True:
#            line = process.stdout.readline()
#            if line != '':
#                #Filter for speed
#                if(line.startswith("Speed")):
#                    list_of_string = line.split()
#                    for i in range(0, len(list_of_string)):
#                        if(is_float(list_of_string[i])):
#                            value = unit_converter(list_of_string[i]+list_of_string[i+1][:-3])
#                            speeds.append(value)
#                            break
#
#            else:
#                break

    com_queue = queue.Queue()

    thread_output = threading.Thread(target=hashcat_out, args=(process, speeds))
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
