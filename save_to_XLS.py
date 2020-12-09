import xlwt
import time
import numpy as np
import os

# TODO: remember to release VideoWriters for all tanks here and delete the refs
#  to them b4 calling this function.
"""
INPUTS:
    strt_time - int (epoch time in s) - start time of the experiment
    tank_dims - np.array, where shape (# of Tanks, 4) - (x_pos,y_pos) pairs for 2 identifying points of each tank
    frame_arr - np.array, where shape (# of Frames in sheet,) - all frames no.s for this sheet
    tstamp_arr - np.array, where shape (same as frame_arr) - all timestamp values for this sheet
    pos_data - np.array, where shape (Tank #, Frame #, 2)
    path_to_save - absolute path of a dir in which to save this .XLS file
"""
def Excel_Save_Rytis(strt_time, tank_dims, frame_arr, tstamp_arr, pos_data, path_to_save, information):
    print("started")
    # TODO: Validate input dimensions
    # tank_dims 2nd dim must be 4
    book = xlwt.Workbook(encoding="utf-8") #create object
    number_of_tanks = tank_dims.shape[0]
    for tank_no in range(number_of_tanks):
        sheet = book.add_sheet("Tank" + str(tank_no + 1)) #add excel sheet
        # Write all the metadata for the tank
        sheet.write(0, 0, "Exp Time")
        # Format for next line:
        sheet.write(0, 1, strt_time) #row, column, string value
        sheet.write(1, 0, "Tank #")
        sheet.write(1, 1, str(tank_no + 1))
        sheet.write(2, 0, "Fish Group")
        sheet.write(2, 1, information[8])
        sheet.write(3, 0, "Fish ID")
        sheet.write(3, 1, information[tank_no])
        sheet.write(4, 0, "Fish DOB")
        sheet.write(4, 1, information[tank_no+4])
        sheet.write(5, 0, "Tank-P1")
        sheet.write(5, 2, int(tank_dims[tank_no][0]))
        sheet.write(5, 3, int(tank_dims[tank_no][1]))
        sheet.write(6, 0, "Tank-P2")
        sheet.write(6, 2, int(tank_dims[tank_no][2]))
        sheet.write(6, 3, int(tank_dims[tank_no][3]))
        sheet.write(7, 0, "FishType")
        sheet.write(7, 1, information[8 + tank_no])
        sheet.write(8, 0, "Camera Width")
        sheet.write(8, 1, information[13])
        sheet.write(9, 0, "Camera Height")
        sheet.write(9, 1, information[14])

        sheet.write(11, 0, "x-y coordinates")
        sheet.write(12, 0, "Frame #")
        sheet.write(12, 1, "Timestamp")
        sheet.write(12, 2, "x")
        sheet.write(12, 3, "y")



        # Write actual data: frame #, timestamp, fish position observations
        # Convoluted - 3 levels of for-loops. TODO: rewrite without 3-level for-loop
        no_of_frames = frame_arr.shape[0]
        for f in range(no_of_frames):
            sheet.write(f + 13, 0, int(frame_arr[f])) # Write Frame No.
            sheet.write(f + 13, 1, tstamp_arr[f]) # Write current tstamp #changed the timestamp from intiger
            sheet.write(f + 13, 2, int(pos_data[tank_no, f, 0])) # Write x_pos for this tstamp
            sheet.write(f + 13, 3, int(pos_data[tank_no, f, 1])) # Write y_pos for this tstamp
            
    #final_path = os.path.join(path_to_save, ('TrackingData_%s_Raw.xls') % (strt_time))
    final_path = os.path.join(path_to_save, (f'TrackingData_{strt_time}_Raw.xls'))
    #final_path = os.path.join(path_to_save, (f'TrackingData_test_Raw.xls'))

    book.save(final_path)
    print("Successfully saved the data")

# --------------------------- TESTS -------------------------------
if __name__ == "__main__":
    time_t1 = time.time()
    tank_dims_t1 = np.random.random_integers(0, 1000, size = (24, 4))
    frame_arr_t1 = np.array(list(range(1, 2001)))
    tstamp_arr_t1 = np.array(list(map(lambda x: x * 2 - 2, list(range(1, 2001)))))

    pos_data_t1 = np.random.random_integers(0, 1000, size=(24, 2000, 2))
    path = os.getcwd()
    Excel_Save_Rytis(time_t1, tank_dims_t1, frame_arr_t1, tstamp_arr_t1, pos_data_t1, path)

# TODO: use xlrd to check the output




        