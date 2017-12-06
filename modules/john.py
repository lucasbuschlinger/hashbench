import subprocess
import threading
import shlex
from .utils import *


# This class encapsulates the functionality to use JohnTheRipper.
class John:

    # Function to capture and filter johns output
    # Required inputs:
    #   process:    the process to read from:           process
    #   speeds:     the list to store the output in     list (mutable)
    # Returns:
    #   mutated list 'speeds' containing (number of cracked hashes, (speed)*)
    @staticmethod
    def __out(process, ignore, speeds=[]):
        # Skipping the first #ignore lines as they are not relevant, except the second.
        for i in range(ignore):
            line = process.stdout.readline()
            if i == 1:
                speeds[1] = int(line.split()[1])
        # Running while process is still running
        while process.poll() is None:
            # Read as long as there is data in stdout
            while True:
                line = process.stdout.readline()

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
    #   hash_type:      type of hash                    string
    #   hash_file:      file containing the hash/hashes string(path)
    #   wordlist:       file containing the wordlist    string(path)
    #   rules:          the rules to be applied         string(path)
    #   max_exec_time:  the maximum time to execute     integer
    # Returns:
    #   list containing (number if cracked hashes, total number of hashes, average speed)
    def wordlist(self, hash_type, hash_file, wordlist, rules, max_exec_time):

        # Arguments for opening the subprocess
        process_args = "./john/run/john --wordlist={} {} --format={} --verbosity=1 --progress-every=1".format(
            wordlist, hash_file, hash_type)

        # Number of lines to skip in output
        skip = 3

        # Adding rules to arguments, if specified
        if rules is not None:
            process_args += " --rules:{}".format(rules)
            skip = 4

        # Adding maximum execution time to arguments, if specified
        if max_exec_time is not None:
            process_args += " --max-run-time={}".format(max_exec_time)

        # Spawn subprocess running an instance of john
        process = subprocess.Popen(shlex.split(process_args), universal_newlines=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        # List to store number of cracked hashes and speeds
        speeds = [0, 0]

        # Calling the output collector
        self.__out(process, skip, speeds)

        # Returning a tuple containing (#cracked hashes, #detected, hashes, average speed)
        return speeds.pop(0), speeds.pop(0), sum(speeds) / len(speeds)

    # Method to brute force hashes with john
    # Required inputs:
    #   hash_type:      type of hash                            string
    #   min:            minimal password length to be tested    integer
    #   max:            maximum password length to be tested    integer
    #   hash_file:      file containing the hash/hashes         string(path)
    #   max_exec_time:  maximum time to execute                 integer
    # Returns:
    #   list containing (number if cracked hashes, total number of hashes, average speed)
    def bruteforce(self, hash_type, min_length, max_length, hash_file, max_exec_time):

        # Arguments for opening the subprocess
        process_args = "./john/run/john --mask=?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a -min-len={} -max-len={} {} --format={}" \
                       " --verbosity=1 --progress-every=1".format(min_length, max_length, hash_file, hash_type)

        # Adding maximum execution time to arguments, if specified
        if max_exec_time is not None:
            process_args += " --max-run-time={}".format(max_exec_time)

        # Spawn subprocess running an instance of john
        process = subprocess.Popen(shlex.split(process_args), universal_newlines=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        # List to store number of cracked hashes and speeds
        speeds = [0, 0]

        # Calling the output collector
        self.__out(process, 4, speeds)

        # Returning a tuple containing (#cracked hashes, #detected, hashes, average speed)
        return speeds.pop(0), speeds.pop(0), sum(speeds) / len(speeds)

    # Method to crack with markov chains
    # Required inputs:
    #   self:           reference to object
    #   hash_type:      type of hash                    string
    #   hash_file:      file containing the hashes      string(path)
    #   max_exec_time:  maximum time to execute         integer
    # Returns:
    #   list containing (number if cracked hashes, total number of hashes, average speed)
    def markov(self, hash_type, hash_file, max_exec_time):

        # Setting a flag whether a maximum execution time was specified
        if max_exec_time is None:
            no_time = True
        else:
            no_time = False

        # Arguments for opening the subprocess
        process_args = "./john/run/john --markov {} --format={} --verbosity=1 --progress-every=1".format(hash_file,
                                                                                                         hash_type)

        # Spawn subprocess running an instance of john
        process = subprocess.Popen(shlex.split(process_args), universal_newlines=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        # List to store number of cracked hashes and speeds
        speeds = [0, 0]

        # Queue to communicate with the timeout thread, enables us to end it, if the process ends prior to timeout
        com_queue = queue.Queue(maxsize=1)

        # This thread capture the output from john
        thread_output = threading.Thread(target=self.__out, args=(process, 4, speeds))
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