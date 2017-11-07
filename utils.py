#Helper to map the given hashtype to the required format by john and hashcat respectively
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

#Helper to check whether the given string is a float
def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

#Helper to convert speed to MH/s
def unit_converter(value):
    if(value.endswith("M")):
        return float(value[:-1])
    else:
        if(value.endswith("K")):
            return float(value[:1])*1000
        elif(value.endswith("G")):
            return float(value[:1])/1000
        elif(value.isdigit()):
            return float(value)*1000*1000
        else:
            #Might want to throw an exception here...
            print("NO VALID TYPE")
