## This tool compares the efficiency of Hashcat and JohnTheRipper on cracking hashes.

Usage: `python3 hashbench.py {hash} {mode} [optional arguments]`


Positional arguments (required):

| argument |    options    | description |
|:--------:|:-------------:|:-----------:|
| hash     |      <=>      | specifies the type of hash the benchmark gets performed on |
|          |      md4      ||
|          |      md5      ||
|          |     sha1      ||
|          |    sha-256    ||
|          |    sha-512    ||
|          |    md5crypt   ||
|   ---    |      ---      | --- |
| mode     |      <=>      | specifies the attack the benchmark gets performed on |
|          |   bruteforce  | perform a brute force attack |
|          |       bf      | short for brute force |
|          |    wordlist   | perform a wordlist attack |
|          |       wl      | short for wordlist ||


___

Optional arguments:

|argument            |  type   |   description |
|:------------------:|:-------:|:------------:|
|-h/--help           |   bool  |   show help message and exit |
|-f/-file            |   str   |   path to a file containing hash(es) |
|-r/-rules           |   str   |   path to rule file for hashcat and rule name for John, needs 2 arguments |
|-t/-time            |   int   |   maximum execution time in seconds |
|-wlf/-wordlistfile  |   str   |   path to wordlist file |
|-minlen             |   int   |   minimum length of password candidates |
|-maxlen             |   int   |   maximum length of password candidates |
|-disablemarkov      |   bool  |   flag to disable markov chains in hashcat (brute force only) |
|-multirun           |   int   |   number of runs to perform on each tool, splits up execution time among runs |
|-individualstats    |   bool  |   flag to print out statistics for individual runs |
|-g/-generate        | int, str|   generates the given amount of new hashes from the supplied files (each run) |

___

## Examples:

__Simple brute force attack:__
`python3 hashbench.py md5 bf -f resources/hashes/top10k.md5 -t 30`
(Runs a 30 minute brute force attack on the MD5-hashes contained in the supplied file)

__To benchmark using a wordlist attack without rules__:
`python3 hashbench.py sha1 wl -f resources/hashes/50k.sha1 -wlf resources/rockyou.wl -t 15`
(Runs a 15 minute wordlist attack on SHA1 using the rockyou wordlist)

__To benchmark using a wordlist attack with rules:__
`python3 hashbench.py md5crypt wl -f resources/hashes/top10k.md5crypt -wlf resources/rockyou.wl -r resources/rules/OneRuleToRuleThemAll.rule OneRuleToRuleThemAll -t 30`
(Runs a 30 minute benchmark on MD5crypt with using the rockyou wordlist and applying the OneRule to it)

__To benchmark with multiple runs on each tool:__
`python3 hashbench.py sha256 bf -f resources/hashes/50k.sha256 -t 30 -multirun 3`
(Runs a 30 minute brute force attack on sha256 and runs each tool three times for 5 minutes each (2 x 3 x 5 = 30))

__To benchmark with freshly generated hashes each run:__
`python3 hashbench.py md5 bf -f resources/hashes/50k.md5 -t 30 -multirun 3 -g 50000 unhashed.pw`
((Runs a 30 minute wordlist attack on md5, running each tool three times for 5 minutes each with 50.000 freshly generated hashes each run)

__To benchmark using the markov mode (JohnTheRipper only):__
`python3 hashbench.py sha512 markov`
(Runs a markov benchmark on SHA-512 with John)

___

A quick word about rules and JohnTheRipper:
In order to use (hashcat) rule files or any other rules you have to specify them in the john.conf in john/run.
To make use of the "OneRule" insert the following :
[//]: # "If you are reading this in plaintext: Don't include the backticks"
```
    [List.Rules:OneRuleToRuleThemAll]
    !! hashcat logic ON
    .include '/ABSOLUTE/PATH/TO/PROJECT/FOLDER/resources/rules/OneRuleToRuleThemAll.rule'
    !! hashcat logic OFF
```
You can alternatively put the rule file in john's run directory, which makes the path easier, for more info see JohnTheRipper's documentation
