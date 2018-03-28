import time
import queue
import statistics
from copy import deepcopy
import configparser
import os.path

"""Lots of helper functions used throughout the project"""


def arg_changer(hash_type):
    """Returns the hash type indicator for the tools"""
    if hash_type == "md5":
        return "raw-md5-opencl", 0
    elif hash_type == 'md4':
        return "raw-md4-opencl", 900
    elif hash_type == 'sha1':
        return "raw-sha1-opencl", 100
    elif hash_type == 'sha-256':
        return "raw-sha256-opencl", 1400
    elif hash_type == 'sha-512':
        return "raw-sha512-opencl", 1700
    elif hash_type == 'md5crypt':
        return 'md5crypt-opencl', 500


def is_float(string):
    """Checks whether value in string is a float"""
    try:
        float(string)
        return True
    except ValueError:
        return False


def unit_converter(value):
    """Converts the given value to MH"""
    if value.endswith("M"):
        return float(value[:-1])
    else:
        if value.endswith("K") or value.endswith("k"):
            return float(value[:-1])/1000
        elif value.endswith("G"):
            return float(value[:-1])*1000
        elif value.isdigit():
            return float(value)/1000/1000
        else:
            # Might want to throw an exception here...
            raise ValueError("Wrong prefix multiplier for H/s given: {}".format(value[:-1]))


def get_default_file(hash_type):
    """Links to default hash files if none is specified"""
    if hash_type == 'md5':
        return "resources/hashes/top10k.md5"
    elif hash_type == 'sha1':
        return "resources/hashes/top10k.sh1"
    elif hash_type == 'sha-256':
        return "resources/hashes/top10k.sha256"
    elif hash_type == 'sha-512':
        return "resources/hashes/top10k.sha512"
    elif hash_type == 'md5crypt':
        return "resources/hashes/top10k.md5crypt"
    else:
        raise Exception('No default file for %s-hashes available! Please supply a file containing hashes!' % hash)


def order_rules(rules):
    """Orders specified rule input for easy handling later on"""
    ordered_rules = []
    if rules is None:
        ordered_rules.append(None)
        ordered_rules.append(None)
        return ordered_rules
    elif rules[0].endswith('.rule'):
        ordered_rules.append(rules[1])
        ordered_rules.append(rules[0])
        return ordered_rules
    else:
        return rules


def trim(speeds, trim_percentage):
    """Trims the list given by x percent"""
    trim_amount = int(len(speeds)*trim_percentage)
    tmpspeeds = sorted(speeds)
    if trim_amount > 1:
        for i in range(0, trim_amount, 2):
            tmpspeeds.pop(0)
            tmpspeeds.pop()
    return tmpspeeds


def concat_speedlists(inputlist, times):
    """Concatenates the lists of speeds produced by the multiple runs.
    Simultaneously removes the first x values where the tools get up to speed.
    """
    tmplist = []
    removed = []
    copy_speeds = deepcopy(inputlist)
    copy_times = deepcopy(times)
    for i in range(len(inputlist)):
        removed.append(remove_startup(copy_times[i], copy_speeds[i]))
        tmplist += copy_speeds[i]
    return tmplist, removed


def remove_startup(times, speeds=[]):
    """Removes the slow speed at the beginning due to the tools getting up to speed"""
    if len(times) == 0 or len(speeds) == 0:
        return 0
    i = 0
    time_first_entry = times[0]
    try:
        median_after = statistics.median(speeds[1:])
        while speeds[0] < median_after * 0.98:
            speeds.pop(0)
            times.pop(0)
            median_after = statistics.median(speeds[1:])
            i += 1
    except (IndexError, statistics.StatisticsError):
        pass
    return round(times[0] - time_first_entry)


def quartiles_range(values):
    """Gets the upper and lower quartile from the list for statistics"""
    tmpvalues = sorted(values)
    entries = len(tmpvalues)
    # Interquartile range only makes sense for a sufficient amount of multiple values
    if entries > 3:
        if entries % 2 == 0:
            lower = int(entries * 0.25)
            upper = int(entries * 0.75)
        else:
            lower = int(entries * 0.25) + 1
            upper = int(entries * 0.75) + 1

        return tmpvalues[upper] - tmpvalues[lower]

    else:
        return 0


def generate_config(config):
    """Generates config file if none if detected"""
    config['HASHBENCH'] = {'location_john': './john/run/john',
                           'location_hashcat': './hashcat/hashcat'}
    with open("hashbench.conf", "w") as configuration_file:
        config.write(configuration_file)

    print("No configuration file was found, generated one. For more info see doc/config.md")


def load_config():
    """Loads the config file"""
    config = configparser.ConfigParser()
    config.read("hashbench.conf")
    if "HASHBENCH" not in config:
        generate_config(config)

    if "location_john" not in config["HASHBENCH"] or "location_hashcat" not in config["HASHBENCH"]\
            or not os.path.isfile(config["HASHBENCH"]["location_john"]) \
            or not os.path.isfile(config["HASHBENCH"]["location_hashcat"]):
        raise ValueError("Configuration for tools not set properly, check configuration file.")

    return config


def duplicate_check(file):
    """Checks the potfiles for duplicate lines/hashes"""
    seen = set()
    duplicates = 0
    try:
        with open(file, "r") as source:
            line = source.readline()
            while line is not '':
                if line in seen:
                    duplicates += 1
                else:
                    seen.add(line)
                line = source.readline()
    except FileNotFoundError:
        print("Potfile {} not found, could not check for duplicates".format(file))
        return 0

    return duplicates
