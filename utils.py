import time
import queue

# Helper to map the given hashtype to the required format by john and hashcat respectively
def arg_changer(hash):
    hashes = []

    if(hash == "md5"):
        hashes.append("raw-md5-opencl")
        hashes.append(0)
    elif(hash == 'md4'):
        hashes.append("raw-md4-opencl")
        hashes.append(900)
    elif(hash == 'sha1'):
        hashes.append("raw-sha1-opencl")
        hashes.append(100)
    elif(hash == 'sha-256'):
        hashes.append("raw-sha256-opencl")
        hashes.append(1400)
    elif(hash == 'sha-512'):
        hashes.append("raw-sha512-opencl")
        hashes.append(1700)

    return hashes


# Helper to check whether the given string is a float
def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# Helper to convert speed to MH/s
def unit_converter(value):
    if(value.endswith("M")):
        return float(value[:-1])
    else:
        if(value.endswith("K") or value.endswith("k")):
            return float(value[:-1])/1000
        elif(value.endswith("G")):
            return float(value[:-1])*1000
        elif(value.isdigit()):
            return float(value)/1000/1000
        else:
            #Might want to throw an exception here...
            print("NO VALID TYPE")


# Helper to supply correct default hashfile to tools, if given
def get_default_file(hash):
    if(hash == 'md5'):
        return "resources/hashes/top10k.md5"
    elif(hash == 'sha1'):
        return "resources/hashes/top10k.sh1"
    elif(hash == 'sha-256'):
        return "resources/hashes/top10k.sha256"
    elif(hash == 'sha-512'):
        return "resources/hashes/top10k.sha512"
    else:
        raise Exception('No default file for %s-hashes available! Please supply a file containing hashes!' % hash)


# Printing own help
def usage():
    f = open('doc/usage.txt', 'r')
    file_contents = f.read()
    print(file_contents)
    f.close()


# Watcher for maximum execution time
def time_watcher(max_exec_time, com_queue):
    if(max_exec_time is None):
        quit()
    start_time = time.time()
    while True and com_queue.empty():
        time_run = time.time() - start_time
        if(time_run > max_exec_time):
            quit()
        time.sleep(1)

# Helper to put specified rules into desired order (john, hashcat)
def rule_orderer(rules):
    ordered_rules = []
    if(rules is None):
        ordered_rules.append(None)
        ordered_rules.append(None)
        return ordered_rules
    elif(rules[0].endswith('.rule')):
        ordered_rules.append(rules[1])
        ordered_rules.append(rules[0])
        return ordered_rules
    else:
        return rules
