#!/usr/bin/env python

# Importing libraries
import os 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ruptures as rpt
from tabulate import tabulate
import glob
import time
import argparse

#---------Declare variables starts---------#
# Declare variables
# input_pressure_sensor_num
# input_temp_sensor_num
# n_input = 2
# step_region = 1000
# pen = 1200
#---------Declare variables ends---------#

def main():
    dirloc = './' # Default: current directory

    parser = argparse.ArgumentParser()

    # Add arguments
    # add argument for input_pressure_sensor_num
    parser.add_argument('-p', '--pnum', type=int, default=1, help='Pressure sensor number (1 or 2), (default=1)')
    parser.add_argument('-t', '--tnum', type=int, default=1, help='Temperature sensor number (1, 2, 3, or 4), (default=1)')
    parser.add_argument('-n', '--ninput', type=int, default=2, help='How many inputs do you want to use? (default=2)')
    parser.add_argument('-s', '--stepreg', type=int, default=1000, help='How many steps do you want to analyze? (default=1000)')
    parser.add_argument('-P', '--pen', type=int, default=1200, help='Penalty value for Pelt algorithm, (default=1200)')
    parser.add_argument('-d', '--dirloc', type=str, default='./', help='Directory location of the csv files, (default=./)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.2.4')
    args = parser.parse_args()

    # Assign arguments to variables
    input_pressure_sensor_num = args.pnum
    input_temp_sensor_num = args.tnum
    n_input = args.ninput
    step_region = args.stepreg
    pen = args.pen
    dirloc = args.dirloc

    #---------argsparse ends---------#

    # Code artwork
    from pyfiglet import Figlet
    f = Figlet(font='slant')
    print(f.renderText('--------'))
    print(f.renderText('PyHLV v 1'))
    print(f.renderText('--------'))
    print('------------------------')
    print('\n')
    print('If you have any questions, please send your questions to my email.')
    print('\nOr, please suggest errors and areas that need updating.')
    print('\n 📨 woo_go@yahoo.com')
    print('\n')
    print('------------------------')
    print('\n')
    time.sleep(1.2)

    # Show user input values
    print('INFO The input_pressure_sensor_num is', input_pressure_sensor_num)
    print('INFO The input_temp_sensor_num is', input_temp_sensor_num)
    print('INFO The n_input is', n_input)
    print('INFO The step_region is', step_region)
    print('INFO The pen is', pen)
    print('INFO The dirloc is', "'" + dirloc + "'")
    time.sleep(1)

    # Ignore warnings
    import warnings
    warnings.filterwarnings(action='ignore')

    # 1. File number and name checking
    file_list = glob.glob(dirloc + '*.csv')
    file_list.sort()
    try:
        if len(file_list) == 0:
            raise Exception
        else:
            pass
    except:
        print("\nINFO There is no csv file in your directory. Please check the directory location.")
        exit()

    # Label file numbers and show all the files
    file_num = []
    for i in range(len(file_list)):
        file_num.append(i)
    print(tabulate({'File number': file_num, 'File name': file_list}, headers='keys', tablefmt='psql'))

    file_number = int(input('INFO These are the files that are in the folder. Please check the file number that you want to use: '))

    # Give one more chance to check the file name
    print("INFO The file name that would be utilized is", file_list[file_number])
    print("INFO Do you want to use this file? (y/n)")

    # define df based on the file number
    df = pd.read_csv(file_list[file_number], encoding='cp949')

    # If the user wants to use the file, then continue the program
    if input() == 'y':
        print("INFO Let's continue the program.")
        pass
    # If the user doesn't want to use the file, then stop the program
    else:
        print("INFO The program has been stopped.")
        exit()

    # 2. Get pressure & temperature data
    pressure = df.iloc[1:,int(input_pressure_sensor_num)+1]
    raw_temp = df.iloc[1:,int(input_temp_sensor_num)+3]
    
    # 3. Note that all data are 'object', therefore, we need to convert them to float
    pressure = pressure.astype(float)
    raw_temp = raw_temp.astype(float)
    temp = raw_temp/10 # Since the raw temperature is in 10x scale, we need to divide it by 10 to get real temperature

    # 4. Reshaping pressure and temperature data into 2D array
    temp = temp.values.reshape(-1,1) 
    pressure = pressure.values.reshape(-1,1)

    #------------------------#
    print('\nINFO The data has been elaborated successfully.')
    #------------------------#

    # 5. Combine pressure and temperature data into one dataframe
    df_flatten = pd.DataFrame({'pressure': pressure.flatten(), 'temperature': temp.flatten()})

    # 6. Apply the two Pelt model and find the rupture point that intersects.
    model = "normal"    
    min_size = 10
    algo = rpt.Pelt(model=model, min_size=min_size).fit(temp)
    result = algo.predict(pen=pen)
    rupture_point = result[-int(n_input)]

    #------------------------#
    print('\nINFO Initialize ruptures algorithm with Pelt model and find the rupture point.')
    #------------------------#

    # 7-1. Plot the rupture plot 
    plt.tight_layout()
    rpt.display(df_flatten, result)
    plt.xlabel('steps', fontsize=10)
    plt.ylabel('Temperature (℃)', fontsize=10, color='k')
    plt.plot(rupture_point, float(df_flatten['temperature'][rupture_point]), 'ro', markersize=8)
    plt.axvline(x=rupture_point, color='r', linestyle='--')
    plt.text(rupture_point, float(df_flatten['temperature'][rupture_point])-2, 'Rupture Point', color='r', fontsize=10)
    plt.savefig('1_finding+ruptures.png', dpi=300)

    # 7-2. Plot the magnified rupture plot
    rpt.display(df_flatten, result)
    plt.xlim(rupture_point-100, rupture_point+100)
    plt.plot(rupture_point, float(df_flatten['temperature'][rupture_point]), 'ro', markersize=8)
    plt.axvline(x=rupture_point, color='r', linestyle='--')
    plt.text(rupture_point, float(df_flatten['temperature'][rupture_point])-2, 'Rupture Point', color='r', fontsize=10)
    plt.figure(figsize=(5,4))
    plt.plot(df_flatten['temperature'], df_flatten['pressure'], 'k')
    plt.xlabel('Temperature (℃)', fontsize=10)
    plt.ylabel('Pressure (bar)', fontsize=10)
    plt.plot(df_flatten['temperature'][rupture_point], df_flatten['pressure'][rupture_point], 'ro', markersize=8)
    plt.axvline(x=df_flatten['temperature'][rupture_point], color='r', linestyle='--')
    plt.savefig('2_P-T_and_rupturepoint.png', dpi=300)
    df_flatten_extracted = df_flatten.iloc[rupture_point-step_region:rupture_point+step_region]

    #------------------------#
    print('\nINFO Finding the final phase EQ point...')
    #------------------------#

    # 8. Define the `ischange` function and execute it. 
    ##########ischange function starts#########
    def ischange(x, y, n):
        # x: temperature
        # y: pressure
        # n: number of points to be examined
        # return: index of the tipping point
        # Find the slope of the line connecting the first and last points
        slope = (y.iloc[-1] - y.iloc[0]) / (x.iloc[-1] - x.iloc[0])
        
        # Find the y-intercept of the line connecting the first and last points
        intercept = y.iloc[0] - slope * x.iloc[0]
        
        # Find the distance between the line connecting the first and last points and the other points
        distance = abs(y - (slope * x + intercept)) / np.sqrt(slope**2 + 1)

        # Find the index of the tipping point
        tipping_point = distance.nlargest(n).index[0]
        return tipping_point
    ##########ischange function ends#########

    # Execute `ischange` function. 
    tipping_point = ischange(df_flatten_extracted['temperature'], df_flatten_extracted['pressure'], 100)

    # 9. Mark the tipping point with the original graph. 
    plt.figure(figsize=(4,3))
    plt.scatter(df_flatten_extracted['temperature'], df_flatten_extracted['pressure'], s=1, color='k')
    plt.plot(df_flatten_extracted['temperature'][tipping_point], df_flatten_extracted['pressure'][tipping_point], 'ro', markersize=5)
    plt.text(df_flatten_extracted['temperature'][tipping_point], df_flatten_extracted['pressure'][tipping_point], 'Onset point', color='r', fontsize=10, fontweight='bold')
    plt.axvline(x=df_flatten_extracted['temperature'][tipping_point], color='r', linestyle='--', linewidth=1, alpha=0.7)
    plt.axhline(y=df_flatten_extracted['pressure'][tipping_point], color='r', linestyle='--', linewidth=1, alpha=0.7)
    plt.plot(df_flatten_extracted['temperature'][rupture_point], df_flatten_extracted['pressure'][rupture_point], 'bo', markersize=5)
    plt.axvline(x=df_flatten_extracted['temperature'][rupture_point], color='b', linestyle='--', linewidth=0.5, alpha=0.8)
    plt.axhline(y=df_flatten_extracted['pressure'][rupture_point], color='b', linestyle='--', linewidth=0.5, alpha=0.8)
    plt.text(df_flatten_extracted['temperature'][rupture_point], df_flatten_extracted['pressure'][rupture_point], 'Rupture point', color='b', fontsize=8)
    plt.xlabel('Temperature (℃)', fontsize=10)
    plt.ylabel('Pressure (bar)', fontsize=10)
    plt.suptitle('Estimated EQ point (scaled)', fontsize=12, fontweight='bold')
    plt.savefig('3_Estimated_EQ_point(scaled).png', dpi=300)

    #10. Combine and express simultaneously the 'Phase EQ Overview' and 'Obtained Phase EQ' graphs into the one graph.
    plt.figure(figsize=(6,4))
    plt.subplot(1,2,1)
    plt.plot(temp, pressure, color='black')
    plt.xlabel('Temperature (℃)')
    plt.ylabel('Pressure (bar)')
    plt.title('1. Overview', fontsize=12, y=1.02, fontweight='bold')
    plt.scatter(float(temp[tipping_point]), float(pressure[tipping_point]), color='r', s=30, marker='o', zorder=10)
    plt.axvline(x=float(temp[tipping_point]), color='r', linestyle='--', linewidth=1)
    plt.axhline(y=float(pressure[tipping_point]), color='r', linestyle='--', linewidth=1)
    plt.subplot(1,2,2)
    plt.plot(temp, pressure, color='blue')
    plt.scatter(float(temp[tipping_point]), float(pressure[tipping_point]), color='r', s=30, marker='o', zorder=10)
    plt.axvline(x=float(temp[tipping_point]), color='r', linestyle='--', linewidth=1)
    plt.axhline(y=float(pressure[tipping_point]), color='r', linestyle='--', linewidth=1)
    plt.xlim(float(temp[tipping_point])-0.5, float(temp[tipping_point])+0.5)
    plt.ylim(float(pressure[tipping_point])-2, float(pressure[tipping_point])+1)
    plt.text(float(temp[tipping_point])+0.1, float(pressure[tipping_point])-0.3, "Phase EQ", fontsize=10, color='r', fontweight='bold')
    plt.text(float(temp[tipping_point])+0.1, float(pressure[tipping_point])-0.5, str(float(pressure[tipping_point]))+" bar", fontsize=9, color='k')
    plt.text(float(temp[tipping_point])+0.1, float(pressure[tipping_point])-0.65, str(float(temp[tipping_point]))+" ℃", fontsize=9, color='k')
    plt.xlabel('Temperature (℃)', color = 'blue')
    plt.ylabel('Pressure (bar)', color = 'blue')
    plt.xticks(color='blue')
    plt.yticks(color='blue')
    ax = plt.gca()
    ax.spines['bottom'].set_color('blue')
    ax.spines['top'].set_color('blue')
    ax.spines['left'].set_color('blue')
    ax.spines['right'].set_color('blue')
    plt.title('2. Magnified View', fontsize=12, y=1.02, fontweight='bold', color='blue')
    plt.suptitle('Phase EQ Diagram', fontsize=16, fontweight='bold', y=1.02)
    plt.subplots_adjust(wspace=0.5)
    plt.tight_layout()
    df_flatten_extracted.to_csv('Phase EQ Data.csv', index=False)
    plt.savefig('4_Phase_EQ_Diagram.png', dpi=300)
    df_tipping_points = pd.DataFrame({'Tipping point': [tipping_point], 'Rupture point': [rupture_point]})
    df_tipping_points.to_csv('Tipping points.csv', index=False)

    #11. Storing and compressing the data
    file_name = os.path.splitext(os.path.basename(file_list[file_number]))[0]
    os.mkdir(file_name)
    import shutil
    shutil.move('Phase EQ Data.csv', file_name)
    shutil.move('4_Phase_EQ_Diagram.png', file_name)
    shutil.move('3_Estimated_EQ_point(scaled).png', file_name)
    shutil.move('2_P-T_and_rupturepoint.png', file_name)
    shutil.move('1_finding+ruptures.png', file_name)
    shutil.move('Tipping points.csv', file_name)
    import shutil
    shutil.make_archive(file_name, 'zip', file_name)
    shutil.rmtree(file_name)

    # 12. Exporting the completion message to user
    #------------------------#
    print('\nINFO The data has been successfully processed and stored in the zip folder named "'+file_name+".zip"+'".')
    time.sleep(1)
    print('\nINFO Make sure to check that the achieved point is your desired phase EQ point.')
    time.sleep(0.8)
    print('\nINFO If not, please input other variables and re-run the program.')
    print('\nINFO For more information, type "pyhlv -h" or "pyhlv --help".')
    #------------------------#  

if __name__ == '__main__':
    main()