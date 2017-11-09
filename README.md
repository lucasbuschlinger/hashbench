Hash Crack Framework [definitely need a better name...]
A framework to benchmark cracking hashes in python(3)

Tools:
  The tools are integrated as git submodules.
  Tool 1 - hashcat:
    - supposed folder: ./hashcat
    - current version: 28/10/17, commit: e6978c23c0f3289abf68fd7f36ee93822012b86c
    - build according to ./hashcat/BUILD.md

  Tool 2 - JohnTheRipper:
    - supposed folder: ./john
    - current version: 01/11/17 commit: 7c4e6d4239ce46f0475449d6589e8c63c91830af
    - build according to ./john/doc/INSTALL-UBUNTU
    - Prerequisites: see ./john/doc/INSTALL-UBUNTU

A real README and documentation will follow later
Very early stage, limited functionality, please forgive me :)

Currently implemented though not optimized:
brute forcing on md5: usage: 'python3 hash_crack_framework.py md5 [-file PATH] mode [-bruteforce | -bf]'
