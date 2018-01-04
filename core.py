import numpy as np
import copy
import warnings


def findTimeIdx(t_lst, t):
    '''Find idx of t in t_lst using binary search

        Parameters:
        --------------------------
        t_lst : list(str)
            List of temporal time stamps
        t : str
            The time stamp we want to find 
    '''    
    
    if t< t_lst[0] or t>t_lst[-1]:
        return None
    else:
        s_idx = 0
        e_idx = len(t_lst)
        while True:
            mid_idx = s_idx + (e_idx-s_idx)/2
            #cur_time = t_lst[mid_idx]
            if t > t_lst[mid_idx]:
                s_idx = mid_idx 
            else:
                e_idx = mid_idx

            if np.abs(s_idx - e_idx) < 3:
                break

        return s_idx



def timeSeriesLst2TimeIntervalLst(tss_lst):

    t_endPoints_lst  = []
    for tss in tss_lst:
        t_endPoints_lst.append([tss.getStartTime(),tss.getEndTime()])
    
    return t_endPoints_lst


def getTimeOverlayMask(t_lst, t_endPoints_lst):
    '''Get the time overlay on time list. 
    (Sample rate of the return mask only depends on 
    the sample rate of the main time stamp signal t_lst)
    
        Parameters:
        -------------------
        t_lst: list(str):
            Main time stamp list that we want to find overlay on.

        t_endPoints_lst: list(list(str,str))
            Time end points for the overlay region.


        Returns:
        -------------------
        1D_array: Mask indicates overlay on main time stamp 
    '''
    msk_arr = np.zeros((len(t_lst),))
    
    for endPoints in t_endPoints_lst:
        
        idx_start = findTimeIdx(t_lst,endPoints[0])
        idx_end = findTimeIdx(t_lst,endPoints[1])
        if idx_start != None and idx_end != None:
            if idx_start == idx_end:
                warnings.warn("Single point mask being detected: Try to smooth the mask using MaskTimeSeriesSeg.smooth()")
                msk_arr[idx_start] = 1
            else:
                assert idx_start < idx_end,\
                'Start index of the time: ' + t_lst[idx_start] + \
                'is greater than the end index of the time: '+ t_lst[idx_start]
                
                msk_arr[idx_start:idx_end] = 1
                

        elif idx_start == None and idx_end != None:
            msk_arr[0:idx_end]=1
        elif idx_end == None and idx_start != None:
            msk_arr[idx_start:] = 1
        else:
            None
    
    return msk_arr



def mergeTimeIntervalLsts(itvl_lsts):
    '''Merge time interval lists into one time interval list
        
        Parameters
        ---------------------------
        itvl_lsts: list(list(tuple)):
            List of time interval lists
    '''
    itvl_dict = {}
    for itvl_lst in itvl_lsts:
        for itvl in itvl_lst:
            # Check if key exists 
            if not ((itvl[0] in itvl_dict) and (itvl[1] < itvl_dict[itvl[0]]) ):
                itvl_dict[itvl[0]] =  itvl[1]

    if bool(itvl_dict):
        #create sorted start time (dict.keys() return a sorted list)
        st_lst_sorted = np.sort(itvl_dict.keys())

       # print st_lst_sorted
        res = []
        start_time = st_lst_sorted[0]
        end_time = itvl_dict[st_lst_sorted[0]]
        
        i = 1
        while i < len(st_lst_sorted):
        
            cur_start_time = st_lst_sorted[i]
            cur_end_time = itvl_dict[st_lst_sorted[i]]
            
            if end_time < cur_start_time:
                res.append((start_time, end_time))
                start_time = cur_start_time
                end_time = cur_end_time

            if end_time >= cur_start_time and end_time < cur_end_time:
                end_time = cur_end_time
                
            i = i + 1

        res.append((start_time,end_time))
        return res
    else:
        return []
    


def rmMaskSingular(mask_arr, singular_size, min_dist):
    '''Remove singular mask points that have distance to others bigger than min_dist
        
        Parameters : 
        -----------------------------------
        mask_arr : 1-d array
        singular_size: int
            Minimum size of the group of the points that can be considered as singular.
        min_dist: int
            Singular group of mask points with distance to other groups < min_dist will be removed.
        
        Returns:
        -----------------------------------
        mask: 1-d array
        
        Example:
        -------------------------------
        [0,1,0,0,0,1,1,1,1,0]->[0,0,0,0,0,1,1,1,1,0]
    
    '''
    assert min_dist >= 2*singular_size,\
    'Singular group is too close to other group: \
     you should either redefine the parameter or use core.mergeMask instead'
    
    msk = copy.deepcopy(mask_arr)
    
    ones = np.ones((singular_size + min_dist,))
    
    i = 0
    while i < msk.shape[0] - singular_size - min_dist-2:
        if msk[i] == 0 and msk[i+1] > 0:
            if np.dot(msk[i: i+ singular_size + min_dist],ones) == singular_size:
                msk[i+1:i+singular_size + 1] = 0
            i = i + singular_size 
        else:
            i = i +1
            
    return msk



def mergeMask(mask_arr, gap_size):
    '''Merge separate masked points that close together to be a continuous mask.
        
        Parameters : 
        -----------------------------------
        mask_arr : 1-d array
        gap_size: int
            The size of the gap when decides merging
        
        Returns:
        -----------------------------------
        merged mask: 1-d array
        
        Example:
        -------------------------------
        [0,0,1,1,0,1,1,0,0]->[0,0,1,1,1,1,1,0,0]
    
    '''
    mask_mg = copy.deepcopy(mask_arr)

    ones = np.ones((gap_size -1,))
    i = 0
    while i < mask_mg.shape[0] - gap_size - 3:
        if mask_mg[i] > 0 and mask_mg[i + 1] == 0:
            if np.dot(mask_mg[i + 1 : i + gap_size],ones) > 0:
                mask_mg[i + 1 : i + gap_size+2] = 1
            i = i + gap_size 
        else:
            i = i +1
    return mask_mg



def msk2Semlst(mask_arr, data_arr, tag_arr):
    """ Map the inference result a list of semantic units
    
        Args:
            mask_arr (array(bool)) : array of occ indicators.
            data_arr (array(int) [number_of_sample_points,]): Acc value of each of the sample points.
            tag_arr (array(string) [number_of_sample_points,]): Time stamp of each of the sample points. 
            stride_size (int): stride size of moving the filter.
        Returns:
            list ([T_array,Y_array]): list of data semantic unit, each unit is a 
                                            continuate recording of when the bridge is in occupancy.
            
    """
    global stride_size

    sem_lst = []

    pre = 0 
    cur = 0
    
    while cur < mask_arr.shape[0]:
        if mask_arr[cur] == mask_arr[pre]:
            cur = cur + 1
        else:
            if mask_arr[cur] == 0 and mask_arr[pre] == 1:
                #tm_itvl = [tag_arr[pre],tag_arr[cur]]
  
                sem_unit_Y = data_arr[pre : cur]
		sem_unit_T = tag_arr[pre : cur]

                sem_lst.append([sem_unit_T, sem_unit_Y])
                
                
                pre = cur
                cur = cur+1
            else:
                pre = cur
                cur = cur+1
                
    return sem_lst

	


