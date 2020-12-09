import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xlrd
import os
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy
from xlutils.save import save

# functions
def get_tank_coordinates(data):
    bot_left_x = data.iloc[4, 2]
    bot_left_y = data.iloc[4, 3]
    top_right_x = data.iloc[5, 2]
    top_right_y = data.iloc[5, 3]
    return bot_left_x, bot_left_y, top_right_x, top_right_y

def data_wrangling(data):
    #rename
    data = data.rename(
        columns={data.columns.values[0]: data.iloc[11,][0], data.columns.values[1]: data.iloc[11,][1]
            , data.columns.values[2]: data.iloc[11,][2], data.columns.values[3]: data.iloc[11,][3]})

    # subset the dataset
    last_row_n = data.shape[0] - 1  # row number
    new_data = data.iloc[12:last_row_n, ]

    # change the indexes
    new_data.index = new_data["Frame #"]
    return new_data

def correct_first_zero(data):
    """
        Inputs:
        data.shape = (Frame #, 4)
        data.columns = Index(['Frame #', 'Timestamp', 'x', 'y'], dtype='object')
        What this does:
        Starts from the first value that is non-zero, makes all previous values the same.
    """
    pd.options.mode.chained_assignment = None  # default='warn' ; Correcting so that false positive SettingWithCopyWarning is not given
    non_zero = data[data["x"] != 0]
    first_x_coordinate = non_zero["x"].iloc[0]
    first_y_coordinate = non_zero["y"].iloc[0]
    index_first_non_zero = non_zero["Frame #"].iloc[0]
    first_zeros = data[data["Frame #"] < index_first_non_zero]  # all the zeros before the first non-zero
    # replace all the zero x,y with non-zero x,y
    first_zeros["x"] = first_x_coordinate
    first_zeros["y"] = first_y_coordinate
    data[data["Frame #"] < index_first_non_zero] = first_zeros

    return data

def correct_last_zero(data):
    """
            Inputs:
            data.shape = (Frame #, 4)
            data.columns = Index(['Frame #', 'Timestamp', 'x', 'y'], dtype='object')
            What this does:
            Starts from the last value that is non-zero, makes all subsequent values the same.
        """
    pd.options.mode.chained_assignment = None
    non_zero = data[data["x"] != 0]
    last_x_coordinate = non_zero["x"].iloc[-1]
    last_y_coordinate = non_zero["y"].iloc[-1]
    index_last_non_zero = non_zero["Frame #"].iloc[-1]
    last_zeros = data[data["Frame #"] > index_last_non_zero]  # all the zeros after the last non-zero
    last_zeros["x"] = last_x_coordinate
    last_zeros["y"] = last_y_coordinate
    data[data["Frame #"] > index_last_non_zero] = last_zeros
    return data

def zero_padding(data):
    """
        Inputs:
        data.shape = (Frame #, 4)
        data.columns = Index(['Frame #', 'Timestamp', 'x', 'y'], dtype='object')
        data must have went through prior cleaning (functions: data_wrangling, correct_first_zero, correct_last_zero)
    """

    # Create an array that is 1 where a is 0, and pad each end with an extra 0.
    iszero = np.concatenate(([0], np.equal(data["x"], 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    # Runs start and end where absdiff is 1
    ranges = np.where(absdiff == 1)[0].reshape(-1,
                                               2)  # array with first element being the index of the beginning of a zero chunk, and second element being the index 1 step after the chunk

    for i in range(0, len(ranges)):
        # index before zero chunk
        before_index = ranges[i][0] - 1
        after_index = ranges[i][1]
        before_index_x = data.iloc[before_index, 2]
        before_index_y = data.iloc[before_index, 3]

        after_index_x = data.iloc[after_index, 2]
        after_index_y = data.iloc[after_index, 3]

        data.iloc[before_index, 1]
        data.iloc[after_index, 1]

        # calculating x_distance
        x_distance = after_index_x - before_index_x
        y_distance = after_index_y - before_index_y

        # just count gap between indices
        elements_chunk = ranges[i][1] - ranges[i][0]
        # divide the distance by those indices
        x_distance_element = x_distance / (elements_chunk + 1)
        y_distance_element = y_distance / (elements_chunk + 1)

        # Interpolation iteration
        count = 0
        for ii in range(ranges[i][0], ranges[i][1]):
            count = count + 1
            x_element_before_chunk = data.iloc[ii - 1, 2]
            y_element_before_chunk = data.iloc[ii - 1, 3]
            data.iloc[ii, 2] = x_element_before_chunk + x_distance_element * count
            data.iloc[ii, 3] = y_element_before_chunk + y_distance_element * count
    return data

def time_in_quadrant(tank_coordinates, data):
    """
    Input -
    data - data.shape (Frame #, 4)
    tank_coordinates - list of length 4 with the coordinates of the tank;

    Output - list(frame_rate, x_mid_point, y_mid_point, s_first_quadrant, s_second_quadrant, s_third_quadrant, s_fourth_quadrant)
    """
    x_mid_point = tank_coordinates[2] - (tank_coordinates[2] - tank_coordinates[0]) / 2
    y_mid_point = tank_coordinates[3] - (tank_coordinates[3] - tank_coordinates[1]) / 2
    first_quadrant = len(data[(data["x"] < x_mid_point) & (data["y"] > y_mid_point)])
    second_quadrant = len(data[(data["x"] < x_mid_point) & (data["y"] < y_mid_point)])
    third_quadrant = len(data[(data["x"] > x_mid_point) & (data["y"] > y_mid_point)])
    fourth_quadrant = len(data[(data["x"] > x_mid_point) & (data["y"] < y_mid_point)])
    frame_rate = sum(data["Timestamp"] <= 1)
    s_first_quadrant = first_quadrant / frame_rate
    s_second_quadrant = second_quadrant / frame_rate
    s_third_quadrant = third_quadrant / frame_rate
    s_fourth_quadrant = fourth_quadrant / frame_rate
    print("Seconds spent in first quadrant: " + str(s_first_quadrant) + " (s)")
    print("Seconds spent in second quadrant: " + str(s_second_quadrant) + " (s)")
    print("Seconds spent in third quadrant: " + str(s_third_quadrant) + " (s)")
    print("Seconds spent in fourth quadrant: " + str(s_fourth_quadrant) + " (s)")
    return frame_rate, x_mid_point, y_mid_point, s_first_quadrant, s_second_quadrant, s_third_quadrant, s_fourth_quadrant

def time_in_dark_white(tank_coordinates, data, tank):
    """
    Input -
    data - data.shape (Frame #, 4)
    tank_coordinates - list of length 4 with the coordinates of the tank;
    tank - the name of the excel sheet (tank name)
    Output - list(frame_rate, x_mid_point, s_dark, s_white)
    """
    x_mid_point = tank_coordinates[2] - (tank_coordinates[2] - tank_coordinates[0]) / 2
    # test which tank it is and select appropriate dark side
    if tank == "Tank3" or tank == "Tank4":
        dark = len(data[(data["x"] > x_mid_point)])
        white = len(data[(data["x"] < x_mid_point)])
    else:
        dark = len(data[(data["x"] < x_mid_point)])
        white = len(data[(data["x"] > x_mid_point)])
    total = len(data["x"])
    percentage_dark = dark / total
    percentage_white = white / total

    print("Percentage of time spent in the dark side: " + str(percentage_dark) + " (%)")
    print("Percentage of timespent in the light side: " + str(percentage_white) + " (%)")
    return x_mid_point, percentage_dark, percentage_white

def dark_first_entry(tank_coordinates, data, tank):
    """
        Input -
        data - data.shape (Frame #, 4)
        tank_coordinates - list of length 4 with the coordinates of the tank;
        tank - the name of the excel sheet (tank name)
        Output - list(frame_rate, x_mid_point, s_first_dark, s_first_crossing, number_entries)
    """
    x_mid_point = tank_coordinates[2] - (tank_coordinates[2] - tank_coordinates[0]) / 2
    frame_rate = sum(data["Timestamp"] <= 1)
    # test which tank it is and select appropriate dark side
    if tank == "Tank3" or tank == "Tank4":
        isdark = np.concatenate(([0], (data["x"] > x_mid_point).view(np.int8), [0]))
    else:
        isdark = np.concatenate(([0], (data["x"] < x_mid_point).view(np.int8), [0]))
    absdiff = np.abs(np.diff(isdark))
    # Runs start and end where absdiff is 1
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    if len(ranges) == 0:
        print("Fish did not enter dark at all")
        # return 0 because fish enters dark for 0 seconds
        return frame_rate, x_mid_point, 0, 0, 0
    else:
        frames_dark = ranges[0][1] - ranges[0][0]
        ### How much time spent in the first dark
        s_first_dark = frames_dark / frame_rate
        ### When was the first entry to dark
        s_first_crossing = ranges[0][0] / frame_rate
        ### How many entries to dark
        number_entries = len(ranges)
        print("Duration of the first entry to dark side: " + str(s_first_dark) + " (s)")
        print("When was the first entry to dark side: " + str(s_first_crossing) + " (s)")
        print("How many times was the dark side enterede: " + str(number_entries))
        return frame_rate, x_mid_point, s_first_dark, s_first_crossing, number_entries

def dark_second_entry(tank_coordinates, data, tank):
    """
        Input -
        data - data.shape (Frame #, 4)
        tank_coordinates - list of length 4 with the coordinates of the tank;
        tank - the name of the excel sheet (tank name)
        Output - list(frame_rate, x_mid_point, s_second_dark)
    """

    x_mid_point = tank_coordinates[2] - (tank_coordinates[2] - tank_coordinates[0]) / 2
    frame_rate = sum(data["Timestamp"] <= 1)
    # test which tank it is and select appropriate dark side
    if tank == "Tank3" or tank == "Tank4":
        isdark = np.concatenate(([0], (data["x"] > x_mid_point).view(np.int8), [0]))
    else:
        isdark = np.concatenate(([0], (data["x"] < x_mid_point).view(np.int8), [0]))
    absdiff = np.abs(np.diff(isdark))
    # Runs start and end where absdiff is 1
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    if len(ranges) == 0:
        print("Fish did not enter dark at all")
        # return 0 because fish enters dark for 0 seconds
        return frame_rate, x_mid_point, 0, 0
    elif len(ranges) == 1:
        print("Fish enter dark only once")
        return frame_rate, x_mid_point, 0, 0
    else:
        frames_dark = ranges[1][1] - ranges[1][0]
        s_second_dark = frames_dark / frame_rate
        ### the time of a second crossing
        s_second_crossing = ranges[1][0] / frame_rate
        print("Duration of second entry to dark side: " + str(s_second_dark) + " (s)")
        print("When was the second entry to dark side: " + str(s_second_crossing) + " (s)")
        return frame_rate, x_mid_point, s_second_dark, s_second_crossing

def plot_locomotion(tank_coordinates, data, path, tank, GroupName):
    """
            Input -
            data - data.shape (Frame #, 4)
            tank_coordinates - list of length 4 with the coordinates of the tank;
            path - the path where the plot should be saved
            tank - the name of the excel sheet (tank)
            GroupName - name of the group

            Output - list(frame_rate, x_mid_point, s_second_dark)
    """
    distance = np.sqrt((np.diff(data["x"].values.astype(float)) ** 2 + np.diff(data["y"].values.astype(float)) ** 2))
    frame_rate = sum(data["Timestamp"] <= 1)
    time = np.diff(data["Frame #"].values.astype(float)) / frame_rate
    velocity = distance / time


    plt.clf() # to avoid duplicated colorbar
    plot = plt.scatter(data["x"][0:-1], data["y"][0:-1], c=velocity, s=1)
    plt.xlabel("x-position")
    plt.ylabel("y-position")
    plt.title(f"Locomotion in {tank} {GroupName}")
    bar = plt.colorbar(plot)
    bar.set_label("Velocity")

    if tank_coordinates[0] > tank_coordinates[2]:
        plt.xlim(right=tank_coordinates[0])
        plt.xlim(left=tank_coordinates[2])
    else:
        plt.xlim(right=tank_coordinates[0])
        plt.xlim(left=tank_coordinates[2])

    if tank_coordinates[1] > tank_coordinates[3]:
        plt.ylim(top=tank_coordinates[1])
        plt.ylim(bottom=tank_coordinates[3])
    else:
        plt.ylim(top=tank_coordinates[3])
        plt.ylim(bottom=tank_coordinates[1])
    #plt.show()

    plt.savefig(os.path.join(path, f'{tank}.png'), bbox_inches="tight")

def plot_locomotion_sides(tank_coordinates, data, distance_from_side, path, tank, GroupName):
    """
                Input -
                data - data.shape (Frame #, 4)
                tank_coordinates - list of length 4 with the coordinates of the tank
                distance_from_side - the number of pixels from the side of a tank (manually designed)
                path - the path where the plot should be saved
                tank - the name of the excel sheet (tank)
                GroupName - name of the group


                Output - list(frame_rate, x_mid_point, s_second_dark)
    """

    distance = np.sqrt((np.diff(data["x"].values.astype(float)) ** 2 + np.diff(data["y"].values.astype(float)) ** 2))
    frame_rate = sum(data["Timestamp"] <= 1)
    time = np.diff(data["Frame #"].values.astype(float)) / frame_rate
    velocity = distance / time

    plt.clf()  # to avoid duplicated colorbar
    plot = plt.scatter(data["x"][0:-1], data["y"][0:-1], c=velocity, s=1)
    plt.xlabel("x-position")
    plt.ylabel("y-position")
    plt.title(f"Locomotion near sides in {tank} {GroupName}")
    bar = plt.colorbar(plot)
    bar.set_label("Velocity")

    if tank_coordinates[0] > tank_coordinates[2]:
        plt.xlim(right=tank_coordinates[0])  # max
        plt.xlim(left=tank_coordinates[2])  # min
    else:
        plt.xlim(right=tank_coordinates[0])
        plt.xlim(left=tank_coordinates[2])

    if tank_coordinates[1] > tank_coordinates[3]:
        plt.ylim(top=tank_coordinates[1])  # max
        plt.ylim(bottom=tank_coordinates[3])  # min
    else:
        plt.ylim(top=tank_coordinates[3])
        plt.ylim(bottom=tank_coordinates[1])

    p1 = (tank_coordinates[0] + distance_from_side, tank_coordinates[1] + distance_from_side)
    p2 = (tank_coordinates[2] - distance_from_side, tank_coordinates[1] + distance_from_side)
    p3 = (tank_coordinates[2] - distance_from_side, tank_coordinates[3] - distance_from_side)
    p4 = (tank_coordinates[0] + distance_from_side, tank_coordinates[3] - distance_from_side)

    plt.axline((p1), (p2), color="r")
    plt.axline((p2), (p3), color="r")
    plt.axline((p3), (p4), color="r")
    plt.axline((p4), (p1), color="r")

    plt.savefig(os.path.join(path, f'{tank}_sides.png'), bbox_inches="tight")

def total_distance_swam(data):
        """
        I measured how many pixels is 1 mm in 1264 x 800 resolution using a real life ruler and imageJ.
        1 mm is 6.4 pixels. This is hardcoded into the analysis when calculating distance.

        """
        distance = np.sqrt((np.diff(data["x"].values.astype(float)) ** 2 + np.diff(data["y"].values.astype(float)) ** 2))
        sum_distance = sum(distance)/6.4 #total distance/ number of pixels in one mm
        return sum_distance

def ten_minute_thigmotaxis_analysis(data, distance_from_side, interval1, interval2, tank_coordinates):
    """
        Input -
        data - data.shape (Frame #, 4)
        tank_coordinates - list of length 4 with the coordinates of the tank;
        distance_from_side - the number of pixels that should be counted from the side of the tank. It is advised that this distance is the length of the fish.
        Fish from 10-14 days are approx. about 7.5mm big. I measured how many pixels 15 mm is in a 1264 x 800 resolution using imageJ.
        15 mm in pixels is 96 pixels. For one fish length the calculation is 48 pixels.
        interval1 - the number of seconds when the first calculation of numbers the fish entered the side is done.
        interval2 - the number of seconds when the second calculation of numbers the fish entered the side is done.

        Output - list(frame_rate, distance_from_side, s_first_side, one_minute_side_enter, ten_minute_side_enter, s_time_side, s_proportion_time)
        """
    frame_rate = sum(data["Timestamp"] <= 1)
    bot_x = (tank_coordinates[0] + distance_from_side)
    top_x = (tank_coordinates[2] - distance_from_side)
    top_y = (tank_coordinates[3] - distance_from_side)
    bot_y = (tank_coordinates[1] + distance_from_side)

    one_minute_data = data[data["Timestamp"] <= interval1]
    ten_minute_data = data[data["Timestamp"] <= interval2]

    isside = np.concatenate(([0], ((one_minute_data["x"] < bot_x) | (one_minute_data["x"] > top_x) | (one_minute_data["y"] < bot_y) | (
                    one_minute_data["y"] > top_y)).view(np.int8), [0]))
    absdiff = np.abs(np.diff(isside))
    one_ranges = np.where(absdiff == 1)[0].reshape(-1, 2)

    isside = np.concatenate(([0], (
                (ten_minute_data["x"] < bot_x) | (ten_minute_data["x"] > top_x) | (ten_minute_data["y"] < bot_y) | (
                    ten_minute_data["y"] > top_y)).view(np.int8), [0]))
    absdiff = np.abs(np.diff(isside))
    ten_ranges = np.where(absdiff == 1)[0].reshape(-1, 2)

    if len(one_ranges) == 0:
        print(f"The fish did not enter the sides in the first minute")
        one_minute_side_enter = 0
    else:
        one_minute_side_enter = len(one_ranges)

    if len(ten_ranges) == 0:
        print(f"The fish did not enter the sides in 10 minutes")
        s_first_side = 0
        ten_minute_side_enter = 0
        s_time_side = 0
    else:
        # first entry to the side
        s_first_side = ten_ranges[0][0] / frame_rate
        # total number of entries at minute 1 and minute 10
        ten_minute_side_enter = len(ten_ranges)
        #  total amount of time spent at the side
        total_time_side = 0
        for range in ten_ranges:
            time_side = range[1] - range[0]
            total_time_side = total_time_side + time_side

        s_time_side = total_time_side / frame_rate

    # calculate the proportion that sides are of the whole tank
    p1 = (tank_coordinates[0], tank_coordinates[1])
    p2 = (tank_coordinates[2], tank_coordinates[1])
    p3 = (tank_coordinates[2], tank_coordinates[3])

    sidep1p2 = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
    sidep2p3 = np.sqrt((p3[0] - p2[0]) ** 2 + (p3[1] - p2[1]) ** 2)

    area = sidep1p2 * sidep2p3

    # p_box is the rectangle that shows the line between inside of tank and sides of tank
    p1_box = (tank_coordinates[0] + distance_from_side, tank_coordinates[1] + distance_from_side)
    p2_box = (tank_coordinates[2] - distance_from_side, tank_coordinates[1] + distance_from_side)
    p3_box = (tank_coordinates[2] - distance_from_side, tank_coordinates[3] - distance_from_side)

    sidep1p2 = np.sqrt((p2_box[0] - p1_box[0]) ** 2 + (p2_box[1] - p1_box[1]) ** 2)
    sidep2p3 = np.sqrt((p3_box[0] - p2_box[0]) ** 2 + (p3_box[1] - p2_box[1]) ** 2)
    area_box = sidep1p2 * sidep2p3

    area_side = area - area_box

    proportion = area_side / area
    # calculate the time it should spend if it was proportional
    s_proportion_time = data["Timestamp"][len(data)] * proportion

    return frame_rate, distance_from_side, s_first_side, one_minute_side_enter, ten_minute_side_enter, s_time_side, s_proportion_time

def create_light_dark_workbook(name):
    """
                        Input -
                        name - the name of your workbook

                        Output - a workbook for storing data
                        """
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet("Light_dark_results")
    tanks = ["Tank1", "Tank2", "Tank3", "Tank4"]  # add back Tank2

    sheet.write(0, 0, "Tank #")
    sheet.write(0, 1, "Light%")
    sheet.write(0, 2, "Dark%")
    sheet.write(0, 3, "Total Distance (mm)")
    sheet.write(0, 4, "Number of entries to dark")
    sheet.write(0, 7, "%")
    sheet.write(0, 8, "Crossing Time first (sec)")
    sheet.write(0, 9, "Duration of first entry (sec)")
    sheet.write(0, 10, "Crossing time second (sec)")
    sheet.write(0, 11, "Duration of second entry (sec)")
    sheet.write(0, 12, "Serial #")
    book.save(str(name))


def light_dark_batch_storing(name, tank, darkwhite, total_distance, first_dark, second_dark, fish_id, i):
    wb = open_workbook(name)
    wb_copy = copy(wb)
    sheet = wb_copy.get_sheet(0)
    sheet.write(i, 0, tank)  # tank number
    sheet.write(i, 1, darkwhite[2])  # %light
    sheet.write(i, 2, darkwhite[1])  # %dark
    sheet.write(i, 3, total_distance)  # total distance
    sheet.write(i, 4, first_dark[4])  # number of entries

    sheet.write(i, 8, first_dark[3])  # Crossing first time
    sheet.write(i, 9, first_dark[2])  # Duration of first entry
    sheet.write(i, 10, second_dark[3])  # Crossing second time
    sheet.write(i, 11, second_dark[2])  # Duration of second entry
    sheet.write(i, 12, fish_id)
    wb_copy.save(name)

def create_thigmotaxis_workbook(name):
    """
                        Input -
                        name - the name of your workbook

                        Output - a workbook for storing data
            """
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet("Thigmotaxis_results")
    tanks = ["Tank1", "Tank2", "Tank3", "Tank4"]  # add back Tank2

    sheet.write(0, 0, "Tank #")
    sheet.write(0, 1, "Serial #")
    sheet.write(0, 2, "First time in side (s)")
    sheet.write(0, 3, "Enter side one minute")
    sheet.write(0, 4, "Enter side ten minute")
    sheet.write(0, 5, "Total time spent in side (s)")
    sheet.write(0, 6, "Proportional total time spent in side (s)")
    book.save(str(name))

def thigmotaxis_batch_storing(name, tank, fish_id, thigmotaxis, ii):
    wb = open_workbook(name)
    wb_copy = copy(wb)
    sheet = wb_copy.get_sheet(0)
    sheet.write(ii, 0, tank)
    sheet.write(ii, 1, fish_id)
    sheet.write(ii, 2, thigmotaxis[2])
    sheet.write(ii, 3, thigmotaxis[3])
    sheet.write(ii, 4, thigmotaxis[4])
    sheet.write(ii, 5, thigmotaxis[5])
    sheet.write(ii, 6, thigmotaxis[6])
    wb_copy.save(name)

#strt_time = "09_Dec_2020_12h25min49s"
#   GroupName = "GroupName"  # delete this
#   path_to_save = 'C:\\Users\\ASM_lab\\Desktop\\Matas_LightDark'
#   group_path = path_to_save + "\\" + GroupName + "_data_" + strt_time
def analysis_Matas (strt_time, GroupName, path_to_save, group_path, track1, track2):
    """
    INPUTS:
        strt_time - time of the experiment. It should be in this format "09_Dec_2020_12h25min49s"
        GroupName - The naming given during the acquisition part. Preferably should be able to tell apart different conditions.
        For example, "Group1_TLEK".
        path_to_save - path to a folder where everything is stored.
        group_path - group-specific path that contains the raw tracking data to analyze, and videos from the acquisition part.
        track1 - Tracker of how many times the analysis was run. This one is for light-dark storage.
        Manually adjust this marker - 0 if first time, 5 if second time, 9 if third time and so on.
        track2 - Tracker of how many times the analysis was run. This one is for thigmotaxis storage.
        Manually adjust this marker - 0 if first time, 5 if second time, 9 if third time and so on.
    Output:
    Analyzed data in a group specific manner of each fish in each tank. Each tank will have the locomotion plotted and information about how much time is spent in quarters.
    This function also analyzes information about light-dark preference of the fish and their preference to spent time near sides.
    The return is outputted in files that contain "batch_results.xls" in them and show the summary statistics of relevant tanks.
    """
    # Read this in as a dictionary - each dictionary is a seperate Tank
    raw_file_name = (f'TrackingData_{strt_time}_Raw.xls')
    os.chdir(group_path)
    all_data = pd.read_excel((raw_file_name), sheet_name=None)
    tanks = ["Tank1", "Tank2", "Tank3", "Tank4"]  # add back Tank2

    # Define where you want to store your analysis folders
    name_folder = (f'Analysis_{GroupName}_{strt_time}')
    folder_path = os.path.join(group_path, name_folder)
    os.mkdir(folder_path)
    # tank = "Tank2" # remove this

    ### Trackers of how many times the analysis was run.

    i = track1  # This is for light-dark storage # 0 if first time, 5 if second time, 9 if third time and so on.
    ii = track2  # This is for thigmotaxis storage

    for tank in tanks:
        data = all_data.get(tank)
        # data.shape # 549, 4

        tank_coordinates = get_tank_coordinates(data)
        fish_id = data.iloc[2, 1]

        data = data_wrangling(data)
        zeros = data[data["x"] == 0]

        print(data[data["x"] == 0].shape[0])  # number of rows where the zero_padding is needed

        # check if correction of zeros is needed when camera did not detect object when it started recording. This is done by checking if the first frame is 0.
        if zeros.iloc[0, 0] == data.iloc[0, 0]:
            data = correct_first_zero(data)

        # check if correction of zeros is needed when camera did not detect object in the end of the recording.
        if data.iloc[data.shape[0] - 1, 0] == zeros.iloc[zeros.shape[0] - 1, 0]:
            data = correct_last_zero(data)

        # zero padding here

        data = zero_padding(data)

        ### test if there is no zeros:
        # zeros = data[data["x"] == 0]
        # zeros

        #### Data analysis:

        # For saving purposes
        directory = (f'{tank}_{GroupName}')
        parent_dir = folder_path
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        filename = os.path.join(path, f'Individual fish plots_{tank}_{GroupName}.txt')
        # 1. time spent in each quadrant
        quadrant = time_in_quadrant(tank_coordinates, data)

        file = open(file=filename, mode="a")
        file.write(f'''Seconds spent in first quadrant: {quadrant[3]} (s)
        Seconds spent in second quadrant: {quadrant[4]} (s)
        Seconds spent in third quadrant: {quadrant[5]} (s)
        Seconds spent in fourth quadrant: {quadrant[6]} (s)\n''')
        file.close()
        # 2. how much time in dark and how much time in white
        # First and second tanks (<) less than x_mid_point
        # Third and fourth tanks (>) more than x_mid_point
        darkwhite = time_in_dark_white(tank_coordinates, data, tank)  # x_mid_point, percentage_dark, percentage_white
        darkwhite[1]
        darkwhite[2]

        # 3. Time of first entry to dark side and how much time they spend there

        first_dark = dark_first_entry(tank_coordinates, data, tank)

        first_dark[2]  # duration of first entry
        first_dark[3]  # the time of first crossing
        first_dark[4]  # number of crossing to dark side

        # 4. Time of 2nd entry and duration of stay

        second_dark = dark_second_entry(tank_coordinates, data, tank)
        second_dark[2]  # Duration fo second entry to dark side
        second_dark[3]  # when was second entry to dark side

        # 5. total distance
        total_distance = total_distance_swam(data)
        # 6. Trajectory after entry to compare locomotion in the dark and the locomotion in the light side.

        # TODO: visualize the two seconds before entering the dark and two seconds after entering the dark

        # 7. Check if swim around the edges

        plot_locomotion_sides(tank_coordinates, data, distance_from_side=30, path=path, tank=tank, GroupName=GroupName)

        # 7 visualize trajectory of swimming + velocity

        plot_locomotion(tank_coordinates, data, path=path, tank=tank, GroupName=GroupName)

        ### For saving for batch analysis of dark entry
        os.chdir(path_to_save)
        name_light_dark = "Light_dark_batch_results.xls"
        if i == 0:
            create_light_dark_workbook(name=name_light_dark)

        i = i + 1
        light_dark_batch_storing(name_light_dark, tank, darkwhite, total_distance, first_dark, second_dark, fish_id, i)

        #### Thigmotaxis analysis - First entry to the sides, how many times the fish when to the side during the first minute
        # how many times the fish when to the side in 10 minute, Total time spent in the side, and what would be a proportional time spent in the side if it was not bias

        thigmotaxis1 = ten_minute_thigmotaxis_analysis(data=data, distance_from_side=48, interval1=60, interval2=600,
                                                       tank_coordinates=tank_coordinates)

        thigmotaxis2 = ten_minute_thigmotaxis_analysis(data=data, distance_from_side=96, interval1=60, interval2=600,
                                                       tank_coordinates=tank_coordinates)
        name_thigmotaxis1 = "Thigmotaxis_1fishlength_batch_results.xls"
        name_thigmotaxis2 = "Thigmotaxis_2fishlength_batch_results.xls"

        if ii == 0:
            create_thigmotaxis_workbook(name=name_thigmotaxis1)
            create_thigmotaxis_workbook(name=name_thigmotaxis2)

        ii = ii + 1
        thigmotaxis_batch_storing(name=name_thigmotaxis1, tank=tank, fish_id=fish_id, thigmotaxis=thigmotaxis1, ii=ii)
        thigmotaxis_batch_storing(name=name_thigmotaxis2, tank=tank, fish_id=fish_id, thigmotaxis=thigmotaxis2, ii=ii)









