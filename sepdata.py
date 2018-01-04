import numpy as np
import core 
import sembrick as sb
import wnfilter as wf

    
def createMeaningfulTimeIntervalLstFromAccel(accel_tss, filter_type = 'threshold_121'):
    '''Create meaninful time interval list from accelTimeSeriesSeg data,
        the filter is learnt in threhold_121 related method'''
    
    
    assert isinstance(accel_tss ,sb.AccelTimeSeriesSeg) == True,\
    'Must be AccelTimeSeriesSeg type'
    
    meaningful_time_interval_lst = []
    
    data_arr = accel_tss.getYArray()
    tag_arr = accel_tss.getTArray()
    
    # Filter data
    if filter_type == 'threshold_121':
        mask_arr,occ_lst = wf.occFilterThres_seg121(data_arr, tag_arr) 
        sem_lst = core.msk2Semlst(mask_arr, data_arr, tag_arr)
    
    #create list of AccelTimeSeriesSeg 
    for sem in sem_lst:
        meaningful_time_interval_lst.append([sem[0][0],sem[0][-1]])
    
    return meaningful_time_interval_lst


def createSinglePersonTimeInterval_OccCamMsk_MeaningfulMsk\
        (t_tss, occ_cam_multy_people_time_intervals,  meaningful_time_intervals):
    '''Generate single person time interval from occ cam mask and meaningful data mask
    
        Parameters:
        ------------------------------
        t_tss: Temporal reference timeSeriesSeg
        occ_cam_multy_people_tss : list([start_time, end_time])
            Time intervals of when occ_cam indicates the number of people > 1
        meaningful_mask_tss :list([start_time, end_time])
        
        Return
        ------------------------
        list([start_time, end_time]): time interval list
    '''
    
        
    assert isinstance(t_tss ,sb.TimeSeriesSeg) == True,\
    'Must be TimeSeriesSeg type'
    
    
    t_tss.addMaskByTimeIntervalLst(meaningful_time_intervals,'meaningful_mask')
    
    t_tss_lst = t_tss.applyMaskByName('meaningful_mask')

    msk = t_tss.getMaskByName('meaningful_mask')

    #### Filter out more than one people case using occ cam data

    t_tss_lst_singlePerson = []

    for elm in t_tss_lst:
        elm.addMaskByTimeIntervalLst(occ_cam_multy_people_time_intervals,'more_people_mask')
        seg_lst = elm.applyMaskByName('more_people_mask')
        #When doesn't detect more than one people
        if seg_lst == []:
            t_tss_lst_singlePerson.append(elm)
    
    return core.timeSeriesLst2TimeIntervalLst(t_tss_lst_singlePerson)
    
    
