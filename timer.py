# Simple Timer
import sys
import time
import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colorbar as cbar
import matplotlib.gridspec as gridspec

# Add functionality:
#    - plot weeks, pick starting day. 
# Improve:
#    - bug: waits for input before plotting heatmap
#    - fix whitespace around plot (change figure size??)

def send_message(message, height):
    screen_height = height - 5
    message_height = message.message_height
    print (screen_height/2)*"\n"
    print message.message
    print ((screen_height/2)-1)*"\n"

def refresh_screen(message):
    os.system(['clear','cls'][os.name == 'nt'])
    width = int(subprocess.check_output(["tput", "cols"]))
    height = int(subprocess.check_output(["tput", "lines"]))
    print "------------------Work Timer V0.3.6---------------".center(width)
    send_message(message, height)
    command = raw_input("Command: ")
    return command

def stamp_time():
    time_array = np.array([time.localtime().tm_hour,
                           time.localtime().tm_min,
                           time.localtime().tm_sec])
    return time_array

def convert_to_secs(time_array):
    time_secs = time_array[0]*(60*60) + time_array[1]*60 + time_array[2]
    return time_secs

def calc_elapsed(start_time, stop_time):
    elapsed_time = convert_to_secs(stop_time) - convert_to_secs(start_time)
    return elapsed_time

def convert_from_secs(secs):
    hours = secs // (60*60)
    secs -= (secs // (60*60))*(60*60)
    mins = secs // 60
    secs -= (secs // 60)*60
    return hours, mins, secs

def convert_to_hours(secs):
    return secs/(60.0*60.0)

def get_dates_times(log_file_address):
    read_file = open(log_file_address, 'r').read().split('\n')
    lines = [s.split('\t') for s in read_file]
    lines.pop(-1)

    for i in range(len(lines)):
        lines[i] = [s.split(',') for s in lines[i]]
        lines[i] = [map(int, s) for s in lines[i]]

    return lines

def calc_time_today(lines):
    today = [time.localtime().tm_year, time.localtime().tm_mon,
             time.localtime().tm_mday]
    time_worked = 0

    for i in range(len(lines)):
        if today == lines[i][0]:
            time_worked += convert_to_hours(calc_elapsed(lines[i][1],
                                                         lines[i][2]))
    return time_worked

def calc_day_times(lines):
    unique_days = []
    day_times = []
    day = lines[0][0]
    unique_days.append(day)
    for i in range(len(lines)):
        if day != lines[i][0]:
            day = lines[i][0]
            unique_days.append(day)

    for days in unique_days:
        time_worked = 0
        for i in range(len(lines)):
            if days == lines[i][0]:
                time_worked += convert_to_hours(calc_elapsed(lines[i][1],
                                                             lines[i][2]))
        day_times.append(time_worked)
        time_worked = 0

    return (unique_days, day_times)

def plot_dates_times(dates, times):
    dates = ["%s-%s-%s" % (s[0], s[1], s[2]) for s in dates]
    index = np.arange(len(times))
    plt.bar(index, times, 0.5)
    plt.ylabel('Hours Worked')
    plt.xlabel('Days')
    plt.title('Daily Hours Worked')
    plt.xticks(index, dates, rotation=60)
    plt.subplots_adjust(bottom=0.22)
    plt.show()

def calc_week_times(start_day):
    # count 7 on from start_day
    pass
            
def convert_to_mins(time_array):
    # Note: minutes with seconds logged are not counted
    time_minutes = 0
    time_minutes += time_array[0]*60
    time_minutes += time_array[1]
    return time_minutes

def count_minutes(start_time, stop_time, day_in_minutes):
    start_min = convert_to_mins(start_time)
    end_min = convert_to_mins(stop_time)

    for i in range(end_min - start_min):
        day_in_minutes[i + start_min] += 1

def normalise_time_count(time_count_array):
    max_count = max(time_count_array)
    min_count = min(time_count_array)
    time_count_array *= 1/(max_count - min_count)
    return time_count_array

def plot_heatmap(times_logged, day_array_in_minutes):
    for times in times_logged:
        count_minutes(times[0], times[1], day_array_in_minutes)

    day_in_minutes = normalise_time_count(day_array_in_minutes)

    gs = gridspec.GridSpec(1, 2, width_ratios=[3,1])
    ax = plt.subplot(gs[0])

    for i, minutes in enumerate(day_in_minutes):
        rect = plt.Rectangle((0,i),1, 1, color=plt.cm.jet(minutes))
        ax.add_patch(rect)

    cax, _  = cbar.make_axes(ax)
    cb2 = cbar.ColorbarBase(cax, cmap=plt.cm.jet)
    ax.set_ylim(0,len(day_in_minutes))
    ax.set_xlim(0,1)
    ax.xaxis.set_visible(False)
    ax.set_ylabel("Hours")
    ax.set_yticks([i for i in range(len(day_in_minutes)) if i % 60 == 0])
    ax.set_yticklabels(["%02d:00" % i for i in range(24)])
    ax.set_title("Heatmap of Time Worked")
    plt.show()

def diagnostic_heatmap(log_file_address):
    dates_times = get_dates_times(log_file_address)
    [i.pop(0) for i in dates_times]
    day_in_minutes = np.zeros((24*60))
    plot_heatmap(dates_times, day_in_minutes)

class Time_Period(object):
    def __init__(self):
        self.date_array = np.array([time.localtime().tm_year,
                                    time.localtime().tm_mon,
                                    time.localtime().tm_mday])
        self.start_time = []
        self.stop_time = []
        self.secs_elapsed = []

    def refresh(self):
        self.start_time = []
        self.stop_time = []
        self.secs_elapsed = []

    def write_to_log(self):
        logFile = open('Log.txt', 'a')
        logFile.write(','.join( [str(item) for item in self.date_array]) + '\t')
        logFile.write(','.join( [str(item) for item in self.start_time]) + '\t')
        logFile.write(','.join( [str(item) for item in self.stop_time]) + '\n')
        logFile.close()
        
class Message(object):
    def __init__(self, message, message_height):
        self.message = message
        self.message_height = message_height

# Main Loop:

welcome_message_text = "Help: type 'b' to start timer, 'f' to stop timer, \n \
            \r 'time' shows total time logged today, 'quit' to exit timer"

welcome_message = Message(welcome_message_text, 2)

log_file_address = 'Log.txt'

x = refresh_screen(welcome_message)
while True:
    if x == 'time':
        hours_worked = calc_time_today(get_dates_times(log_file_address))
        time_worked = "You have worked for %.1f hours today." % hours_worked
        time_message = Message(time_worked, 1)
        x = refresh_screen(time_message)

    elif x == 'b':
        time_instance = Time_Period()
        time_instance.start_time = stamp_time()
        begin_timer_message_text = "Clocked In!"
        begin_message = Message(begin_timer_message_text, 1)
        x = refresh_screen(begin_message)

    elif x == 'f':
        time_instance.stop_time = stamp_time()
        time_instance.write_to_log()
        time_instance.refresh()
        end_timer_message_text = "Cocked Out! Time Logged."
        end_message = Message(end_timer_message_text, 1)
        x = refresh_screen(end_message)
        
    elif x == 'heatmap':
        heatmap_open_message_text = "Plotting Heatmap..."
        heatmap_open_message = Message(heatmap_open_message_text, 1)
#        refresh_screen(heatmap_open_message)
        diagnostic_heatmap(log_file_address)
        heatmap_close_message_text = "Heatmap Closed."
        heatmap_close_message = Message(heatmap_close_message_text, 1)
        x = refresh_screen(heatmap_close_message)

    # Used to test functions:
    elif x =='test':
        test_message_text = "Testing Feature."
        test_message = Message(test_message_text, 1)
        d, t = calc_day_times(get_dates_times(log_file_address))
        plot_dates_times(d, t)
        time.sleep(5)
        x = refresh_screen(test_message)

    elif x == 'quit':
        break

    else:
        unknown_message_text = "Unknown Command."
        unknown_message = Message(unknown_message_text, 1)
        x = refresh_screen(unknown_message)


