import subprocess
import time
from utils import *

#Method to brute force hashes with john
#Required inputs:
#   hash: type of hash, string
#   min: minimal password length to be tested, integer
#   max: maximum password length to be tested, integer
#   hash_file: file containing the hash/hashes
def john_bruteforce(hash, min, max, hash_file):

    #Spawn subprocess running an instance of john
    process = subprocess.Popen(["./john/run/john", "--mask=?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a", "-min-len={}".format(min), "-max-len={}".format(max), hash_file, "--format={}".format(hash), "--verbosity=1", "--progress-every=1"], universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    #List to store the collected speeds
    speeds = []

    #Getting output from john while process is running
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

    #Return average speed
    return sum(speeds)/len(speeds)

####################################################################################################

#Method to brute force hashes with hashcat
#Required inputs:
#   hash: type of hash, integer
#   min: minimal password length to be tested, integer
#   max: maximum password length to be tested, integer
#   hash_file: file containing the hash/hashes
def hashcat_bruteforce(hash, min, max, hash_file):

    #Spawn subprocess running an instance of hashcat
    process = subprocess.Popen(["./hashcat/hashcat", "-m", "{}".format(hash), "-a3", "--increment", "--increment-min", "{}".format(min), "--increment-max", "{}".format(max), hash_file ,"?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a", "--status", "--status-timer", "1"],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    #List to store the collected speeds
    speeds = []

    while(process.poll() == None):
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
        #Wait for 0.5seconds, enough data is generated anyways
        time.sleep(0.5)

    #Return average speed
    return sum(speeds)/len(speeds)
