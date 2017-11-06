import subprocess

def john_bruteforce():
    print("")

def hashcat_bruteforce(hash, min, max):
    #process = subprocess.Popen(["./john/run/john", "--test", "--format={}".format(hash[0])], stdout=subprocess.PIPE)
    #print("###########")
    #while(process.poll() == None):
    #    out, err = process.communicate()
    #    print(out)
    #print("###########")
    temp_file = open("temp.txt", "a")
    process = subprocess.Popen(["./hashcat/hashcat", "-m", "{}".format(hash), "-a3", "--increment", "--increment-min", "{}".format(min), "--increment-max", "{}".format(max), "hashcat/example0.hash","?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a"],  universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    while(process.poll() == None):
        process.stdin.write("s")
        process.stdin.close()
        while True:
            line = process.stdout.readline()
            if line != '':
                if(line.startswith("Speed")):
                    print(line.rstrip())
                else:
                    #process.stdout.close()
                    break


hashcat_bruteforce(0, 4, 6)
