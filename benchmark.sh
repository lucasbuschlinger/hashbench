#!/bin/bash
# Execute this in the same directory as hashbench

python3 hashbench.py md5 bf -g 1000000 resources/rockyou.wl -t 60 -multirun 3
echo -------------------------------------------
python3 hashbench.py md5crypt bf -f resources/hashes/50k.md5crypt -t 60 -multirun 3
echo -------------------------------------------
python3 hashbench.py md5 wl -g 5000000 resources/rockyou.wl -wlf resources/rockyou.wl -t 60 -multirun 3
echo -------------------------------------------
python3 hashbench.py md5 wl -g 5000000 resources/rockyou.wl -wlf resources/rockyou.wl -r resources/rules/OneRuleToRuleThemAll.rule OneRuleToRuleThemAll -t 60 -multirun 3
echo -------------------------------------------
python3 hashbench.py md5 wl -g 5000000 resources/rockyou.wl -wlf resources/rockyou.wl -r resources/rules/hashcat_korelogic.rule KoreLogic -t 60 -multirun 3
