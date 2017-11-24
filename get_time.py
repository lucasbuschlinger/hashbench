def main():

    with open("time_spent.txt") as f:
        lines = f.readlines()
    time_min = 0
    for line in lines:
        words = line.split()
        time_min += int((words[-1])[:-3])
    time_hrs = time_min/60

    print("Total time spent:")
    print("  %d minutes" % time_min)
    print("  %.2f hours" % time_hrs)


main()
