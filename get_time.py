from decimal import *


def main():

    with open("time_spent.txt") as f:
        lines = f.readlines()
    time_min = 0
    for line in lines:
        words = line.split()
        time_min += int((words[-1])[:-3])
    time_hrs = Decimal(time_min/60).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    print("Total time spent:")
    print(str(time_min) + " minutes")
    print(str(time_hrs) + " hours")


main()
