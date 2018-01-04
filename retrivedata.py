import numpy as np
import wnfilter as wf
import csv
import sembrick as sb
import data360Production

        
def readAccelFromServer(pier9_bridge_info, sensor_name ,start_time, end_time):
    '''Return AccelTimeSeriesSeg from server

        Parameters
        ----------------------------
        sensor_name: str
        start_time:str
        end_time:str

        Returns
        -----------------------------
        AccelTimeSeries

        Examples
        ------------------------------
        readStrainFromServer('pi-pier9-bridge-accel-0-4-a-y-4',
                                '2017-04-27T12:00:00.000Z',
                                2017-04-27T12:00:10.000Z')
    '''

    assert ('accel' in sensor_name) == True, 'Error in sensor name, must be accel sensor.'

    data360Production.init()

    #start_ts = '2017-04-27T12:00:00.000Z'
    #end_ts = '2017-04-27T12:00:10.000Z'

    server_reading = data360Production.get_readings( pier9_bridge_info[0],\
                                                pier9_bridge_info[1], \
                                                pier9_bridge_info[2],\
                                                [sensor_name],\
                                                start_time, end_time)


    return serverRead2AccelTSS(server_reading, sensor_name)


def readStrainFromServer( pier9_bridge_info,sensor_name ,start_time, end_time):
    '''Return StrainTimeSeriesSeg from server

        Parameters
        ----------------------------
        sensor_name: str
        start_time:str
        end_time:str

        Returns
        -----------------------------
        StrainTimeSeries

        Examples
        ------------------------------
        readStrainFromServer('pi-pier9-bridge-accel-0-4-a-y-4',
                                '2017-04-27T12:00:00.000Z',
                                2017-04-27T12:00:10.000Z')                 
    '''

    assert ('strain' in sensor_name) == True, 'Error in sensor name, must be strain sensor.'

    data360Production.init()
    server_reading = data360Production.get_readings( pier9_bridge_info[0],\
                                          pier9_bridge_info[1], \
                                          pier9_bridge_info[2],\
                                          [sensor_name],\
                                          start_time, end_time)

    return serverRead2StrainTSS(server_reading, sensor_name)

    
def readSinglePersonMaskOccCamFromServer(pier9_bridge_info, sensor_name ,start_time, end_time):
    '''Return MaskTimeSeriesSeg of a single person on occ cam

        Parameters
        ----------------------------
        sensor_name: str
        start_time:str
        end_time:str

        Returns
        -----------------------------
        MaskTimeSeriesSeg

        Examples
        ------------------------------
        readSinglePersonMaskOccCamFromServer('test-env-cam-1-occ,
                                            '2017-04-27T12:00:00.000Z',
                                            2017-04-27T12:00:10.000Z')                 
                '''

    assert ('cam' in sensor_name) == True, 'Error in sensor name, must be strain sensor.'

    data360Production.init()
    server_reading = data360Production.get_readings( pier9_bridge_info[0],\
                                          pier9_bridge_info[1], \
                                          pier9_bridge_info[2],\
                                          [sensor_name],\
                                          start_time, end_time)

    return serverRead2OccCamSingleMaskTSS(server_reading, sensor_name)


    
def readMultyPeopleMaskOccCamFromServer(pier9_bridge_info, sensor_name ,start_time, end_time):
    '''Return MaskTimeSeriesSeg of a single person on occ cam 

        Parameters
        ----------------------------
        sensor_name: str
        start_time:str
        end_time:str

        Returns
        -----------------------------
        MaskTimeSeriesSeg

        Examples
        ------------------------------
        readMultyPeopleMaskOccCamFromServer('test-env-cam-1-occ,
                                            '2017-04-27T12:00:00.000Z',
                                            2017-04-27T12:00:10.000Z')                 
                '''
    assert ('cam' in sensor_name) == True, 'Error in sensor name, must be strain sensor.'

    data360Production.init()
    server_reading = data360Production.get_readings( pier9_bridge_info[0],\
                                          pier9_bridge_info[1], \
                                          pier9_bridge_info[2],\
                                          [sensor_name],\
                                          start_time, end_time)

    return serverRead2OccCamMultyMaskTSS(server_reading, sensor_name)


    
def serverRead2StrainTSS(server_reading, sensor_name):
    tag_list = []
    data_list = []
    for row in server_reading['readingList']:
        tag_list.append(row['ts'])
        data_list.append(float(row['val']))
    return sb.StrainTimeSeriesSeg((np.asarray(tag_list), np.asarray(data_list)),sensor_name)


def serverRead2OccCamSingleMaskTSS( server_reading, sensor_name):
    tag_list = []
    data_list = []
    for row in server_reading['readingList']:
        tag_list.append(row['ts'])
        data_list.append(int(row['val']))

    tag_arr = np.asarray(tag_list)
    data_arr = np.asarray(data_list)

    for i in range(data_arr.shape[0]):
        if data_arr[i] > 1:
            data_arr[i] = 0 

    return sb.MaskTimeSeriesSeg((tag_arr, data_arr),sensor_name)

    
def serverRead2OccCamMultyMaskTSS(server_reading, sensor_name):
    tag_list = []
    data_list = []
    for row in server_reading['readingList']:
        tag_list.append(row['ts'])
        data_list.append(int(row['val']))

    tag_arr = np.asarray(tag_list)
    data_arr = np.asarray(data_list)

    for i in range(data_arr.shape[0]):
        if data_arr[i] <= 1:
            data_arr[i] = 0
        else:
            data_arr[i] = 1


    return sb.MaskTimeSeriesSeg((tag_arr, data_arr),sensor_name)

    
def serverRead2AccelTSS(server_reading, sensor_name):
    tag_list = []
    data_list = []
    for row in server_reading['readingList']:
        tag_list.append(row['ts'])
        data_list.append(int(row['val']))
    return sb.AccelTimeSeriesSeg((np.asarray(tag_list), np.asarray(data_list)),sensor_name)

    
def readAccelFromLocal( csv_file_name, sensor_name):
    '''Return AccelTimeSeriesSeg'''
    tag_arr, data_arr = convertAccelDataFromCSV(csv_file_name)
    return sb.AccelTimeSeriesSeg((tag_arr, data_arr),sensor_name)


def readStrainFromLocal( csv_file_name, sensor_name):
    '''Return StrainTimeSeriesSeg'''
    tag_arr, data_arr = convertStrainDataFromCSV(csv_file_name)
    return sb.StrainTimeSeriesSeg((tag_arr, data_arr),sensor_name)


def readSinglePersonMaskOccCamFromLocal( csv_file_name, sensor_name):
    '''Return MaskTimeSeriesSeg'''
    tag_arr, data_arr = convertOccCamDataFromCSV(csv_file_name)

    for i in range(data_arr.shape[0]):
        if data_arr[i] > 1:
            data_arr[i] = 0 

    return sb.MaskTimeSeriesSeg((tag_arr, data_arr),sensor_name)

def readMultyPeopleMaskOccCamFromLocal( csv_file_name, sensor_name):
    '''Return AccelTimeSeriesSeg'''
    tag_arr, data_arr = convertOccCamDataFromCSV(csv_file_name)

    for i in range(data_arr.shape[0]):
        if data_arr[i] <= 1:
            data_arr[i] = 0
        else:
            data_arr[i] = 1

    return sb.MaskTimeSeriesSeg((tag_arr, data_arr),sensor_name)



def convertOccCamDataFromCSV(accel_data_filename):
    """Get occ-cam series data in csv to array
    Args:
        accdata_filename (string): csv data file name from accelerometer sensor.
    Returns:
        array: Array of name stamp
        array: Array of data cast to int
    """
    with open(accel_data_filename) as csvfile:
        readCSV = csv.reader (csvfile,delimiter=',')
        tag_list = []
        data_list = []
        for row in readCSV:
            tag_list.append(row[0])
            data_list.append(int(row[1]))

    return np.asarray(tag_list), np.asarray(data_list)



def convertAccelDataFromCSV(accel_data_filename):
    """Get accel-time series data in csv to array
    Args:
        accdata_filename (string): csv data file name from accelerometer sensor.
    Returns:
        array: Array of name stamp
        array: Array of data cast to int
    """
    with open(accel_data_filename) as csvfile:
        readCSV = csv.reader (csvfile,delimiter=',')
        tag_list = []
        data_list = []
        for row in readCSV:
            tag_list.append(row[0])
            data_list.append(int(row[1]))

    return np.asarray(tag_list), np.asarray(data_list)



def convertStrainDataFromCSV(strain_data_filename):
    """Get strain-time series data in csv to array
    Args:
        accdata_filename (string): csv data file name from accelerometer sensor.
    Returns:
        array: Array of name stamp
        array: Array of data cast to int
    """
    with open(strain_data_filename) as csvfile:
        readCSV = csv.reader (csvfile,delimiter=',')
        tag_list = []
        data_list = []
        for row in readCSV:
            tag_list.append(row[0])
            data_list.append(float(row[1]))


    return np.asarray(tag_list), np.asarray(data_list)


