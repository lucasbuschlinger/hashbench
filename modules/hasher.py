import hashlib
import random


def generate_hashes(source, amount, hash_type):
    """Calls the specific hashers.
    Trade-off here was (almost) repetitive code vs rather confusing if/else-ing.
    """
    if hash_type == "md5":
        __genMD5(source, amount)
    elif hash_type == "sha1":
        __genSHA1(source, amount)
    elif hash_type == "sha256":
        __genSHA256(source, amount)
    elif hash_type == "sha512":
        __genSHA512(source, amount)
    else:
        raise ValueError("Requested hash {} not available for generation".format(hash_type))


def __genMD5(source, amount):
    used_indices = []
    with open("gen.hash", "w") as dest:
        with open(source, "r") as src:
            words = src.readlines()
            size = len(words)
            if amount > size:
                print("Warning: Source file for new hashes contains less entries than requested hashes,"
                      " only generating {} hashes".format(size))
                amount = size
            for i in range(amount):
                hasher = hashlib.md5()
                x = random.randint(0, size - 1)
                while x in used_indices:
                    x = random.randint(0, size - 1)
                word = words[x].replace("\n", "")
                hasher.update(word.encode())
                new_hash = hasher.hexdigest()
                dest.write(new_hash + "\n")


def __genSHA1(source, amount):
    used_indices = []
    with open("gen.hash", "w") as dest:
        with open(source, "r") as src:
            words = src.readlines()
            size = len(words)
            if amount > size:
                print("Warning: Source file for new hashes contains less entries than requested hashes,"
                      " only generating {} hashes".format(size))
                amount = size
            for i in range(amount):
                hasher = hashlib.sha1()
                x = random.randint(0, size - 1)
                while x in used_indices:
                    x = random.randint(0, size - 1)
                word = words[x].replace("\n", "")
                hasher.update(word.encode())
                new_hash = hasher.hexdigest()
                dest.write(new_hash + "\n")


def __genSHA256(source, amount):
    used_indices = []
    with open("gen.hash", "w") as dest:
        with open(source, "r") as src:
            words = src.readlines()
            size = len(words)
            if amount > size:
                print("Warning: Source file for new hashes contains less entries than requested hashes,"
                      " only generating {} hashes".format(size))
                amount = size
            for i in range(amount):
                hasher = hashlib.sha256()
                x = random.randint(0, size - 1)
                while x in used_indices:
                    x = random.randint(0, size - 1)
                word = words[x].replace("\n", "")
                hasher.update(word.encode())
                new_hash = hasher.hexdigest()
                dest.write(new_hash + "\n")


def __genSHA512(source, amount):
    used_indices = []
    with open("gen.hash", "w") as dest:
        with open(source, "r") as src:
            words = src.readlines()
            size = len(words)
            if amount > size:
                print("Warning: Source file for new hashes contains less entries than requested hashes,"
                      " only generating {} hashes".format(size))
                amount = size
            for i in range(amount):
                hasher = hashlib.sha512()
                x = random.randint(0, size - 1)
                while x in used_indices:
                    x = random.randint(0, size - 1)
                word = words[x].replace("\n", "")
                hasher.update(word.encode())
                new_hash = hasher.hexdigest()
                dest.write(new_hash + "\n")