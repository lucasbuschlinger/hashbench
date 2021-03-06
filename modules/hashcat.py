import subprocess
import threading
import queue
import shlex
from .utils import *


class Hashcat:
    """This class encapsulates all functionality used to run benchmarks with Hashcat."""

    @staticmethod
    def __out(process, q):
        """This function collects the output generated by Hashcat.

        Arguments:
            process (process):  the subprocess which is hashcat
            q       (Queue):    queue to communicate with the runner

        Returns:
            This returns all values via the passed queue.
            Values are:
                Number of cracked hashes
                Number of detected hashes
                List of recorded speeds
                List of points in time where the speeds were recorded
        """

        cracked = detected = 0
        speeds = []
        times = []
        start = time.time()
        # Only collecting while process in running (poll == None) and no signal to quit has been received via the queue
        while process.poll() is None and q.empty():
            list_of_string = process.stdout.readline().split()
            time_of_status = time.time() - start
            # Only considering STATUS lines its format can be found at
            # https://hashcat.net/wiki/doku.php?id=machine_readable
            if 'STATUS' in list_of_string:
                times.append(time_of_status)
                detected = int(list_of_string[-8])
                cracked = int(list_of_string[-9])
                speed = 0
                # First speed is always at fourth position
                index = 3
                while True:
                    speed += int(list_of_string[index])
                    index += 2
                    # Next speed would be 2 positions further, if its NaN ('EXEC_RUNTIME') we're done
                    if not is_float(list_of_string[index]):
                        break
                speeds.append(speed/1000000)
        # Emptying queue if signal was received
        if not q.empty():
            q.get()
        q.put(cracked)
        q.put(detected)
        q.put(speeds)
        q.put(times)

    def execute(self, location, mode, hash_type, hash_file, max_exec_time, wordlist, rules, min_len, max_len,
                no_markov):
        """This function runs the benchmark with hashcat.
            It constructs the commandline with the correct arguments as they are specified.

        Arguments:
            location        (string):   location of hashcat binary
            mode            (int):      mode flag
            hash_type       (int):      hash type flag
            hash_file       (string):   path to hash file
            max_exec_time   (int):      seconds to run at most
            wordlist        (string):   path to wordlist
            rules           (string):   path to rule file
            min_len         (int):      minimum candidate length
            max_len         (int):      maximum candidate length
            no_markov       (bool):     flag to disable hashcat's markov chains


        Returns:
            The values received from the output reader which are:
            Number of cracked hashes
            Number of detected hashes
            List of recorded speeds
            List of points in time where the speeds were recorded
        """

        # Default maximum runtime is 10h
        if not max_exec_time:
            max_exec_time = 36000

        process_args = location

        # Mode 1 = Brute Force, Mode 0 = Wordlist
        if mode:
            process_args += " -m {} -a3 --increment --increment-min {} --increment-max {}" \
                       " {} ?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a -w 3 -O --machine-readable" \
                       " --quiet -o /dev/null".format(hash_type, min_len, max_len, hash_file)
            if no_markov:
                process_args += " --markov-disable"
        else:
            process_args += " -a0 -m{} {} {} -w 3 -O -o /dev/null --machine-readable --quiet".format(
                hash_type, hash_file, wordlist)
            if rules:
                process_args += " -r {}".format(rules)

        # Spawning the subprocess running an instance of hashcat
        process = subprocess.Popen(shlex.split(process_args), universal_newlines=True, stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE, encoding='utf-8', errors='ignore')

        q = queue.Queue()

        out_thread = threading.Thread(target=self.__out, args=(process, q))
        out_thread.start()

        start = time.time()
        time_run = 0
        # While the process and its output reading thread are running as well not having reached the maximum execution
        # time we send it input to get more output
        while out_thread.is_alive() and time_run < max_exec_time and q.empty():
            process.stdin.write("s")
            process.stdin.flush()
            time.sleep(0.1)
            time_run = time.time() - start
        process.kill()
        # Signaling output reading thread if it is still running (the queue will be empty then)
        if q.empty():
            q.put(0)
        out_thread.join()

        # Fetching values from queue
        cracked = q.get()
        detected = q.get()
        speeds = q.get()
        times = q.get()

        return cracked, detected, speeds, times
