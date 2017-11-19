import subprocess
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
        while True:
            line = process.stdout.readline()
            if line != '':
                # Filter for speed
                if(line.startswith("Speed")):
                    list_of_string = line.split()
                    speed = unit_converter(list_of_string[1]+list_of_string[2][:-3])
                    speeds.append(speed)
                # Filter for number of cracked hashes
                elif(line.startswith("Recovered.")):
                    list_of_string = line.split()
                    list_of_string = list_of_string[1].split('/')
                    speeds[0] = int(list_of_string[0])

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
        process = subprocess.Popen(["./hashcat/hashcat", "-a0", "-m", "{}".format(hash), hash_file, wordlist, "--status", "--status-timer", "1", "-w", "3", "-O""--runtime={}".format(max_exec_time), "-o", "/dev/null"],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    else:
        # Spawn subprocess running an instance of hashcat with rules
        process = subprocess.Popen(["./hashcat/hashcat", "-a0", "-m", "{}".format(hash), hash_file, wordlist, "--status", "--status-timer", "1", "-r", "-w", "3", "-O",rules, "--runtime={}".format(max_exec_time), "-o", "/dev/null"],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # List to store number of cracked hashes and speeds
    speeds = [0]

    # Calling the output collector
    hashcat_out(process, speeds)

    # Putting number of cracked hashes into returning value
    return_values = [speeds.pop(0)]
    # Appending average speed to returning value
    return_values.append(sum(speeds)/len(speeds))

    return return_values


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
    process = subprocess.Popen(["./hashcat/hashcat", "-m", "{}".format(hash), "-a3", "--increment", "--increment-min", "{}".format(min), "--increment-max", "{}".format(max), hash_file ,"?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a", "--status", "--status-timer", "1", "-w", "3", "-O", "--runtime={}".format(max_exec_time), "-o", "/dev/null"],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # List to store number of cracked hashes and speeds
    speeds = [0]

    # Calling the output collector
    hashcat_out(process, speeds)

    # Putting number of cracked hashes into returning value
    return_values = [speeds.pop(0)]
    # Appending average speed to returning value
    return_values.append(sum(speeds)/len(speeds))

    return return_values
