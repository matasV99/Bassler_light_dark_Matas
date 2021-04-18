# Bassler_light_dark_Matas


There are 3 files that are necessary to do light_dark and thigmotaxis analysis using a Bassler camera: "Plotting_light_dark.py", "save_to_XLS.py", "Bassler_Light_dark_assay". The main script is "Bassler_Light_dark_assay" which uses openCV and pypylon packages to acquire image from the camera and track fish through the method of background subtraction. This script calls two external functions - Excel_Save_Rytis and analysis_Matas. Excel_Save_Rytis saves the output from "Bassler_Light_dark_assay" in an .xls file. analysis_Matas file does a) data cleaning to interpolate for 0 values when the camera lost track of the subject b) Ploting locomotion of each individual fish c) Analysis of Light-dark paradigm d) Analysis of Thigmotaxis paradigm e) Saving of the latter analyses in excel files.

For the pipeline to work, the three files mentioned above have to be in the same folder. The pipeline is also only compatible with Windows OS because it uses os package to manage paths. 
