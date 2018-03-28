import matplotlib
matplotlib.use('Agg')  # Needed for when no display is available
import matplotlib.pyplot as plotter
import matplotlib.gridspec as gridspec
import numpy
import datetime
from statistics import median, StatisticsError


def plot_speeds(john_speeds, hashcat_speeds, john_times, hashcat_times):
    """Plots the speed graphs in a grid layout and saves plot to a .png file.

        Arguments:
            john_speeds     (list): list of recorded speeds for john
            hashcat_speeds  (list): list of recorded speeds for hashcat
            john_times      (list): list of time points where john's speeds were recorded
            hashcat_times   (list): list of time points where hashcat's speeds were recorded
    """
    runs = len(john_speeds)
    row_scale = 10
    col_scale = 5
    if runs == 1:
        rows = 1
        cols = 1
    elif runs == 2:
        rows = 1
        cols = 2
        col_scale = col_scale / 2
    elif runs == 3:
        rows = 2
        cols = 2
    else:
        rows = int(runs/2)
        cols = runs - rows
    grid = gridspec.GridSpec(rows, cols)
    plotter.figure(1, figsize=(rows * row_scale, cols * col_scale))
    for i in range(runs):
        try:
            john_avg = median(john_speeds[i])
            hashcat_avg = median(hashcat_speeds[i])
        except StatisticsError:
            print("Could not generate speed plot - did not received no data")
            return
        max_avg = 3 * max(john_avg, hashcat_avg)
        plotter.subplot(grid[i])
        # Limiting plot on y-Axis if extreme outliers are in data
        if max(john_speeds[i] + hashcat_speeds[i]) > max_avg:
            plotter.ylim(0, max_avg)
        plotter.plot(john_times[i], john_speeds[i], label='John\'s speeds (Average: %.3f MH/s)' % john_avg)
        plotter.plot(hashcat_times[i], hashcat_speeds[i], label='Hashcat\'s speeds (Average: %.3f MH/s)' % hashcat_avg)
        plotter.ylabel('MH/s')
        plotter.xlabel('seconds')
        plotter.title('Speeds of run {}'.format(i + 1))
        plotter.legend(loc='best')
    plotter.subplots_adjust(hspace=0.5)
    time = datetime.datetime.now().time()
    date = datetime.date.today()
    outfile = "speeds-{0:02d}:{1:02d}:{2:0d}-{3:02d}:{4:02d}.png".format(date.day, date.month, date.year, time.hour,
                                                                         time.minute)
    plotter.savefig(outfile)


def plot_cracked(john, hashcat, detected):
    """Plots the amount of cracked hashes as a bar plot and saves plot to a .png file

        Arguments:
            john        (list): list containing how many hashes john cracked
            hashcat     (list): list containing how many hashes hashcat cracked
            detected    (int):  maximum number of hashes detected in hash file by either of the tools
    """
    row_scale = 7
    col_scale = 7
    width = 0.35
    runs = len(john)
    x_labels = []
    for i in range(runs):
        x_labels.append("Run #{}".format(i + 1))
    indices = numpy.arange(runs)
    figure, axis = plotter.subplots(1, figsize=(row_scale, col_scale))
    axis.bar(indices, john, width, label='John')
    axis.bar(indices+width, hashcat, width, label='Hashcat')
    axis.legend(loc='best')
    axis.set_xticks(indices + width / 2)
    axis.set_xticklabels(x_labels)
    axis.autoscale_view()
    plotter.title("Cracked hashes per run (of %d detected)" % detected)
    plotter.ylabel("Cracked hashes")
    time = datetime.datetime.now().time()
    date = datetime.date.today()
    outfile = "cracked-{0:02d}:{1:02d}:{2:0d}-{3:02d}:{4:02d}.png".format(date.day, date.month, date.year, time.hour,
                                                                          time.minute)
    plotter.savefig(outfile)
