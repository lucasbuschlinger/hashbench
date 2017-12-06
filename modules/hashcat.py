import subprocess
import threading
import queue
import shlex
from .utils import *


# This class encapsulated the functionality to use hashcat.
class Hashcat:

    # Function to capture and filter hashcat's output
    # See https://hashcat.net/wiki/doku.php?id=machine_readable to understand
    # Required inputs:
    #   process:    the process to read from            process
    #   speeds:     the list to store the output in     list (mutable)
    # Returns:
    #   mutated list 'speeds' (number of cracked hashes, (speed)*)
    # noinspection PyDefaultArgument
    @staticmethod
    def __out(process, speeds=[]):
        # Flag for writing total number of detected hashes
        written = False
        # Running while process is still running
        while process.poll() is None:
            # Read as long as there is data in stdout
            while True:
                line = process.stdout.readline()
                if line != '':
                    list_of_string = line.split()
                    # Omitting non status lines
                    if list_of_string[0] == 'STATUS':
                        speed = 0
                        # First speed is always at fourth position
                        index = 3
                        while True:
                            speed += int(list_of_string[index])
                            index += 2
                            # Next speed would be 2 positions further, if its NaN ('EXEC_RUNTIME') we're done
                            if not is_float(list_of_string[index]):
                                break
                        speeds.append(speed)
                        # Number of recovered hashes is 8 positions further from 'EXEC_RUNTIME'
                        speeds[0] = int(list_of_string[index+8])
                        # Writing number of detected hashes, if not already done
                        if not written:
                            speeds[1] = int(list_of_string[index+9])

                else:
                    break

        # Returning the mutated list containing the recorded values
        return speeds

    # Method to perform a wordlist attack with hashcat
    # Required inputs:
    #   hash_type:      type of hash                        integer
    #   hash_file:      file containing the hash/hashes     string(path)
    #   wordlist:       file containing the wordlist        string(path)
    #   rules:          the rules to be applied             string(path)
    #   max_exec_time:  the maximum time to execute         integer
    # Returns:
    #   list containing (number if cracked hashes, total number of hashes, average speed)
    def wordlist(self, hash_type, hash_file, wordlist, rules, max_exec_time):

        # Arguments for opening the subprocess
        process_args = "./hashcat/hashcat -a0 -m{} {} {} --status --status-timer 1 -w 3 -O -o /dev/null" \
                       " --machine-readable --quiet".format(hash_type, hash_file, wordlist)

        # Adding rules to arguments, if specified
        if rules is not None:
            process_args += " -r {}".format(rules)

        # Adding maximum execution time to arguments, if specified
        if max_exec_time is not None:
            process_args += " --runtime={}".format(max_exec_time)

        process = subprocess.Popen(shlex.split(process_args), universal_newlines=True, stdout=subprocess.PIPE)

        # List to store number of cracked hashes and speeds
        speeds = [0, 0]

        # Calling the output collector
        self.__out(process, speeds)

        # Returning a tuple containing (#cracked hashes, #detected, hashes, average speed)
        return speeds.pop(0), speeds.pop(0), sum(speeds) / len(speeds)

    # Method to brute force hashes with hashcat
    # Required inputs:
    #   hash_type:           type of hash                             integer
    #   min:            minimal password length to be tested     integer
    #   max:            maximum password length to be tested     integer
    #   hash_file:      file containing the hash/hashes          string(path)
    #   max_exec_time:  the maximum time to execute              integer
    # Returns:
    #   list containing (number if cracked hashes, total number of hashes, average speed)
    def bruteforce(self, hash_type, min_length, max_length, hash_file, max_exec_time, no_markov):

        # Flag to specify whether a max execution time was given
        if max_exec_time is None:
            no_time = True
        else:
            no_time = False

        # Arguments for opening the subprocess
        process_args = "./hashcat/hashcat -m {} -a3 --increment --increment-min {} --increment-max {}" \
                       " {} ?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a --status --status-timer 1 -w 3 -O --machine-readable" \
                       " --quiet -o /dev/null".format(hash_type, min_length, max_length, hash_file)

        # Adding flag to disable markov chains to arguments, if specified
        if no_markov:
            process_args += " --markov-disable"

        # Spawn subprocess running an instance of hashcat
        process = subprocess.Popen(shlex.split(process_args), universal_newlines=True, stdout=subprocess.PIPE)

        # List to store number of cracked hashes and speeds
        speeds = [0, 0]

        com_queue = queue.Queue(maxsize=1)

        # This thread captures the output from hashcat
        thread_output = threading.Thread(target=self.__out, args=(process, speeds))
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
        thread_output.join()

        # Terminating timeout thread if hashcat is done earlier
        if thread_timeout.is_alive():
            com_queue.put("Exit")
        thread_timeout.join()

        # Returning a tuple containing (#cracked hashes, #detected, hashes, average speed)
        return speeds.pop(0), speeds.pop(0), sum(speeds) / len(speeds)
