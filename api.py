import numpy as np
#import matplotlib.pyplot as plt
#%matplotlib inline

import wnfilter as wf
import sembrick as sb
import retrivedata as rd
import core

def createOccTimeSerieSegFromAccel(accel_tss_seg, accel_tss_seg_lst, occ_sensor_name):
    '''Create occ data from accel data and its meaningful seg list
    
        Parameters:
        ---------------------
        tss_seg: AccelTimeSeriesSeg
            The main signal we want to find occ mask on.

        accel_tss_seg_lst: list(AccelTimeSeriesSeg)
            The list of meaningful segments from the main signal

        occ_sensor_name: str
            Name of the sensor

        Returns: 
        --------------------
        MaskTimeSeriesSeg

    '''
    
    # Check type
    type_correct = 1
        
    if not isinstance(accel_tss_seg, AccelTimeSeriesSeg):
        type_correct = 0
       
    for seg in accel_tss_seg_lst:
        if not isinstance(seg,AccelTimeSeriesSeg):
            type_correct = 0
            break
            
    assert type_correct == 1,\
    "Type error: Need AccelTimeSeriesSeg type and list(AccelTimeSeriesSeg) type"
    
    occ_T = accel_tss_seg.getTArray()
    t_lst = occ_T.tolist()
    t_endPoints_lst  = []
    for seg in accel_tss_seg_lst:
        if accel_tss_seg.getSensorName() == seg.getSensorName():
            t_endPoints_lst.append([seg.getStartTime(),seg.getEndTime()])

    occ_Y = core.getTimeOverlayMask(t_lst, t_endPoints_lst)

    assert occ_T.shape[0] == occ_Y.shape[0], "Not same length"

    time_series_data = [occ_T, occ_Y]

    return MaskTimeSeriesSeg(time_series_data, occ_sensor_name)
    



def getMeaningfulStrainFromAccel_CSV(strain_file_name, accel_file_name_lst, strain_sensor_name):
    '''Get meaningful data on strain sensor using 
    occ data got from data on accel sensors

    Parameters:
    ------------------
    strain_file_name : str
    accel_file_name_lst : 

    Returns:
    ----------------
    list(StrainTimeSeriesSeg)
    
    Eamples:
    -----------------------------------------------------------------------------------
    strain_file_name = './pi-pier9-bridge-strain-1-right-s-0-readings.csv'

    z2_data_file_name = './MSensors/pi-pier9-bridge-accel-0-4-a-z-2-readings.csv'
    z1_data_file_name = './MSensors/pi-pier9-bridge-accel-0-4-a-z-1-readings.csv'
    accel_file_name_lst = [z1_data_file_name,z2_data_file_name]

    strain_sensor_name = 'pi-pier9-bridge-strain-1-right-s-0'

    strain_lst = getMeaningfulStrainFromAccel_CSV(strain_file_name, accel_file_name_lst, strain_sensor_name)

    '''
    
    i = 0
    lst_of_time_interval_lst = []
    for accel_file_name in accel_file_name_lst:
           
        sensor_name = 'accel_temp_sensor'
        
        accel_tss = rd.readAccelFromLocal(accel_file_name, sensor_name)

        # Create tss data list from tss data (Use filter to get meaningful data) 
        accel_lst_creator = sb.AccelSegListCreator()
        accel_mngfl_lst = accel_lst_creator.createMeaningfulSegList(\
                                            accel_tss, sensor_name, 'threshold_121')

        lst_of_time_interval_lst.append(sb.timeSeriesLst2TimeIntervalLst(accel_mngfl_lst))
    
    
    time_interval_lst_merged = sb.mergeTimeIntervalLsts(lst_of_time_interval_lst)

    #Get strain tss data from the data base
    strain_tss = rd.readStrainFromLocal(strain_file_name, strain_sensor_name)
    
    #Add and apply mask
    strain_tss.addMaskByTimeIntervalLst(time_interval_lst_merged,'occ_strain')
    strain_tss_lst = strain_tss.applyMaskByName('occ_strain')

    return strain_tss_lst


