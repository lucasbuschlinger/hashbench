# HashBench
_A framework to benchmark cracking hashes, written in Python 3._  
It does so by using actual test data one has to supply instead of using the integrated benchmark modes.
___
### Tools:
The tools are integrated as git submodules.

Tool 1 - hashcat:
- [Their github](https://github.com/hashcat/hashcat)
- tested version from 3 March 2018, commit: f6cfcbb (latest version on 28 March)
- build according to hashcat/BUILD.md

Tool 2 - JohnTheRipper (Community version, _**bleeding**_ branch!):
- [Their github](https://github.com/magnumripper/JohnTheRipper)
- tested version from 27 March 2018, commit: e4e1571 (latest version on 28 March)
- build according to john/doc/INSTALL-UBUNTU
- Prerequisites: see john/doc/INSTALL-UBUNTU

The paths to each tool's executables can be set in the hashbench.conf
(defaults are ./hashcat/hashcat and ./john/run/john respectively).

For usage see [doc/usage.md](doc/usage.md)

---
If you discover any bugs, please don't refrain from opening up issues.
