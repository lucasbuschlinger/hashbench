#!/bin/bash
# Execute this in the same directory as hashbench

python3 hashbench.py md5 bf -g 50000 resources/rockyou.wl -t 60 -multirun 5
python3 hashbench.py md5crypt bf -g 50000 resources/rockyou.wl -t 60 -multirun 5
python3 hashbench.py md5 wl -g 100000 resources/rockyou.wl -wlf resources/rockyou.wl -r resources/rules/OneRuleToRuleThemAll.rule OneRuleToRuleThemAll -t 60 -multirun 5
