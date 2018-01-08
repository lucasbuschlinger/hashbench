import time
import datetime

def main():

    with open("time_spent.txt") as f:
        lines = f.readlines()
    time_min = 0
    for line in lines:
        words = line.split()
        time_min += int((words[-1])[:-3])
    time_hrs = time_min//60
    time_min_ = time_min % 60

    today = time.strftime("%x")
    month = int(today[1])
    day = int(today[3:5])
    year = 2018
    current_week = datetime.date(year, month, day).isocalendar()[1]
    target_week = datetime.date(2018, 3, 31).isocalendar()[1]
    remaining_weeks = target_week - current_week + 1
    total_time = 180 * 60
    time_left = total_time - time_min
    hrs_left = 180 - time_hrs
    min_left = (60 - time_min_) % 60

    if min_left > 0:
        hrs_left -= 1

    hrs_per_week = time_left / remaining_weeks // 60
    min_per_week = time_left / remaining_weeks % 60

    print("Total time spent:")
    print("  %d minutes" % time_min)
    print("   = %d:%02dh" % (time_hrs, time_min_))
    print("\n%d weeks until deadline, %d:%02dh remain" % (remaining_weeks, hrs_left, min_left))
    print("  => There should be about %d:%02dh be done per week to reach the 180h goal" % (hrs_per_week, min_per_week))


main()
