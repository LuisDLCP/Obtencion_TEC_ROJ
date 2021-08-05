#!/usr/bin/python3.6
import pandas as pd
import datetime
import glob
import os 

current_path = "/home/cesar/Desktop/luisd/scripts/Obtencion_TEC/"
input_files_path = current_path + "data_input/Data_set/"
input_files_path_op = current_path + "data_input/Data_procesada/"
output_files_path = current_path + "data_output/"

# Read ISMR files
def readISMR(input_file_name):
    # Read ismr file
    data = pd.read_csv(input_files_path+input_file_name, header=None, squeeze=True)
    return data

# Convert an ISMR to LISN format file
def imsr2TEC(data):
    # Extract data
    WN = data[0] # Week number, since first epoch
    TOW = data[1] # Time of week (s)
    SVN = data[2]

    # Create the HEADER columns as lists
    yr = [] # year
    dyr = [] # day_year
    sd = [] # seconds_day
    prn = [] # prn
    for i in range(len(WN)):
        fecha = WeekSeconds2UTC(int(WN[i]), int(TOW[i]), 0)
        yr.append(fecha["year"])
        dyr.append(fecha["day_year"])
        sd.append(fecha["seconds_day"])
        prn.append(get_PRN(int(SVN[i])))

    # Create the HEADER dataframe by joining the column lists
    list_tuples = list(zip(yr,dyr,sd,prn)) # creates a list of tuples
    dataFrame = pd.DataFrame(list_tuples, columns=['year','day','seconds','PRN']) # creates a pandas dataframe

    # Adding other pandas series(BODY)
    dataFrame['alpha'] = data[4]
    dataFrame['epsilon'] = data[5]
    dataFrame['TEC-45'] = data[16] # TEC at TOW-45s
    dataFrame['TEC-30'] = data[18] # TEC at TOW-30s
    dataFrame['TEC-15'] = data[20] # TEC at TOW-15s
    dataFrame['TEC-0'] = data[22] # TEC at TOW
    dataFrame['dTEC-60'] = data[17] # dTEC from TOW-60s to TOW-45s
    dataFrame['dTEC-45'] = data[19] # dTEC from TOW-45s to TOW-30s
    dataFrame['dTEC-30'] = data[21] # dTEC from TOW-30s to TOW-15s
    dataFrame['dTEC-15'] = data[23] # dTEC from TOW-15s to TOW
    
    # Create the final dataFrame
    def create_rowDataFrame(seconds):
        # Select a subset of data
        subset1 = dataFrame[dataFrame["seconds"] == seconds]
        # Create the list header
        header = list(subset1.iloc[0,:3])
        header.append(len(subset1))
        # Create the list body
        ss1 = subset1.loc[:,"PRN":] # Select some columns
        # Merge the list header and body
        for i in range(len(ss1)):
            header += list(ss1.iloc[i])
        # Create the row dataframe
        parameters = pd.DataFrame([header])

        return parameters

    seconds_list = dataFrame['seconds']
    seconds_list = list(seconds_list.drop_duplicates())

    for i in range(len(seconds_list)):
        if i == 0:
            result = create_rowDataFrame(seconds_list[i])
        else:
            result = result.append(create_rowDataFrame(seconds_list[i]),ignore_index=True)
    result = result.round(3) # round decimal numerical values to 3 numbers

    return result

# Convert GPS time: week & seconds; to UTC time.
# OJO: It's missing the leapseconds, these value get from the navigation file
def WeekSeconds2UTC(gpsweek,gpsseconds,leapseconds):
    datetimeformat = "%Y-%m-%d %H:%M:%S"
    first_epoch = datetime.datetime.strptime("1980-01-06 00:00:00",datetimeformat)
    elapsed = datetime.timedelta(days=(gpsweek*7),seconds=(gpsseconds-leapseconds))

    # LISN date format: 2 digit year, day of year, seconds since midnight for a day
    date = datetime.datetime.strftime(first_epoch + elapsed,"%y-%j;%H:%M:%S")

    year = int(date[:2])
    day_year = int(date[3:6])
    hour = int(date[7:9])
    minute = int(date[10:12])
    second = int(date[13:15])
    seconds_day = second*1 + minute*60 + hour*60*60

    return {"year":year, "day_year":day_year, "seconds_day": seconds_day}

# Convert SVIDs to PRN codes. The PRNs code were obtained from PolaRx5S Reference Guide.
def get_PRN(svid):
    if 1<=svid<=37:
        prn = "G"+str(svid)
    elif 38<=svid<=61:
        prn = "R"+str(svid-37)
    elif svid==62:
        prn = "NA"
    elif 63<=svid<=68:
        prn = "R"+str(svid-38)
    elif 71<=svid<=106:
        prn = "E"+str(svid-70)
    elif 107<=svid<=119:
        prn = "NA"
    elif 120<=svid<=140:
        prn = "S"+str(svid-100)
    elif 141<=svid<=177:
        prn = "C"+str(svid-140)
    elif 181<=svid<=187:
        prn = "J"+str(svid-180)
    elif 191<=svid<=197:
        prn = "I"+str(svid-190)
    elif 198<=svid<=215:
        prn = "S"+str(svid-157)
    elif 216<=svid<=222:
        prn = "I"+str(svid-208)
    else:
        prn = "svid not valid!"

    return prn

# Generate lisn format file name
def get_file_name(file_name): # filename: ljic2710.20_.ismr
    station_name = file_name[:4] # ljic 
    #igs15 = file_name[-12:-9] # 15 minutes prefixe 

    YY = file_name[9:11] # 20
    DOY = file_name[4:7] # 271
    today = YY + "-" + DOY # e.g. '21-271'
    fecha = datetime.datetime.strptime(today,"%y-%j")
    fecha2 = datetime.datetime.strftime(fecha,"%y-%m-%d") #e.g. '20-08-06'
    year = fecha2[:2]
    month = fecha2[3:5]
    day = fecha2[6:8]

    tec_file_name = station_name + "_" + year + month + day + ".dat"

    return tec_file_name

def save_csv(file_name, value):
    TEC_name = get_file_name(file_name)
    # Save dataFrame to csv file
    value.to_csv(output_files_path+TEC_name, sep='\t',index=False,header=False,encoding='utf-8')
    return "Ok"

def main():
    list_input_files = glob.glob(input_files_path+'*.ismr')
    if len(list_input_files)>0:
        for file_i in list_input_files:
            file_name = file_i[len(input_files_path):] # Get the file's name

            dframe_ismr = readISMR(file_name)
            dframe_lisn = imsr2TEC(dframe_ismr)
            save_csv(file_name, dframe_lisn)

            # Move input files to a permanent directory
            os.rename(file_i, input_files_path_op+file_name)

if __name__ == '__main__':
    print("Getting started ...")
    main()
    print("Finished!")
