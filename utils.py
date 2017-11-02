def arg_changer(hash):
    hashes = []

    if(hash == "md5"):
        hashes.append("raw-md5-opencl")
        hashes.append("0")
    elif(hash == 'md4'):
        hashes.append("raw-md4-opencl")
        hashes.append("900")
    elif(hash == 'sha1'):
        hashes.append("raw-sha1-opencl")
        hashes.append("100")
    elif(hash == 'sha-256'):
        hashes.append("raw-sha256-opencl")
        hashes.append("1400")
    elif(hash == 'sha-512'):
        hashes.append("raw-sha512-opencl")
        hashes.append("1700")
    
    return hashes
