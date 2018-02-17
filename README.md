# HashBench
_A framework to benchmark cracking hashes, written in in Python 3._
___
### Tools:
The tools are integrated as git submodules.

Tool 1 - hashcat:
- [Their github](https://github.com/hashcat/hashcat)
- tested version: 28/01/18, commit: 9aa9725b9104702355465fb4a778c4ef8420a250
- build according to hashcat/BUILD.md

Tool 2 - JohnTheRipper (Community version, _**bleeding**_ branch!):
- [Their github](https://github.com/magnumripper/JohnTheRipper)
- tested version: 28/01/18 commit: ac09fca621bb83b9fc16c59e999cb41b0ef072b9
- build according to john/doc/INSTALL-UBUNTU
- Prerequisites: see john/doc/INSTALL-UBUNTU

The paths to each tool's executables can be set in the hashbench.conf
(defaults are ./hashcat/hascat and ./john/run/john respectively)

For usage see [doc/usage.md](../blob/doc/usage.md)
