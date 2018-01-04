import numpy as np
from scipy import signal
import scipy
import copy
import core


stride_size = 40



def inf2Occ_helper(inference_res, tag_arr, seg_size):
    """ Map the inference result back to the origianl points sampled on temporal domain.
        This is the helper function for occFilter.
    
        Args:
            inference_res (array(int) [num_of_data,]): Array of inference result for the data semantic units.
            tag_arr (array(string) [number_of_sample_points,]): Time stamp for each of the sample points. 
            stride_size (int): stride size of moving the filter.
        Returns:
            array(bool): array of occupancy indicator.
            list([string,bool]): list of time stamp and the occupancy indicator.
            
    """
    #Get edge case padding
    global stride_size
    front_padding = []
    edge_padding_len =  stride_size/2 + seg_size/2
    if inference_res[0] == 0:
        front_padding.append(np.zeros((edge_padding_len,)))
    else:
        front_padding.append(np.ones((edge_padding_len,)))
    
    
    occ_mask_lst = []
    for i in range(1,inference_res.shape[0]):
        if inference_res[i] == 0:
            occ_mask_lst.append(np.zeros((stride_size,)))
        else:
            occ_mask_lst.append(np.ones((stride_size,)))
    
    total_length = (len(occ_mask_lst))*stride_size 
    
    stride_arr = np.reshape(occ_mask_lst, (total_length))
    
    front_padding_arr = np.reshape(front_padding,(edge_padding_len,))
    
    mask_arr = np.concatenate((front_padding_arr, stride_arr), axis=0)

    occ_lst = []  
    for i in range(mask_arr.shape[0]):
        if mask_arr[i] == 1:
            occ_lst.append([tag_arr[i], 1])
            
    return mask_arr, occ_lst


def infThres_seg121(data_arr):
    """Get clean meaningful data here"""
    inf_lst = []
    i = 0
    
    data_meaningful_clean = []
    var_arr = np.var(data_arr, axis=0).astype(int)
    
    #t1=time.time()
    fft_arr = np.fft.fft2(data_arr)
    #print time.time()- t1
    
    fft_arr_abs = abs(fft_arr[1:,:]).astype(int)
    
    fft_arr_abs_max = np.max(fft_arr_abs, axis = 0)
    
    fft_arr_abs_sum = np.sum(fft_arr_abs>20, axis = 0)

    while i < data_arr.shape[1]:
        maxamp = fft_arr_abs_max[i]
        sal20 = fft_arr_abs_sum[i]
        var = var_arr[i]
        if  maxamp > 65 and var > 1 and sal20 > 10:
            data_meaningful_clean.append(data_arr[:,i])
            inf_lst.append(True)
        else:
            inf_lst.append(False)
        i= i+1
    
    return np.asarray(inf_lst), np.asarray(data_meaningful_clean)



def occFilterThres_seg121(data_arr, tag_arr):
    
    """ Map occ filter on acc data.
    
        Args:
            data_arr (array(int) [number_of_sample_points,]): Acc value of each of the sample points.
            tag_arr (array(string) [number_of_sample_points,]): Time stamp of each of the sample points. 
            stride_size (int): stride size of moving the filter.
        Returns:
            array(bool): array of occupancy indicator.
            list([string,bool]): list of time stamp and the occupancy indicator.
            
    """
    global stride_size 
    
    segment_size = 121
    
    data_length = data_arr.shape[0]
    start_idx = 0
    
    data_seg_lst = []
    
    # Cut data into peices as a 2D data matrix for inference 
    while start_idx + segment_size < data_length:

        data_seg_lst.append(data_arr[start_idx:start_idx + segment_size])
        
        start_idx = start_idx + stride_size 
            
    data_seg_arr = np.asarray(data_seg_lst)
    
    # Inference the 2D data matrix
    #t1=time.time()
    inf_arr, data_meaningful_clean = infThres_seg121(np.transpose(data_seg_arr))
    #print time.time()- t1
    mask_arr, occ_lst = inf2Occ_helper(inf_arr, tag_arr, segment_size)
    
    ex_pad = 80
    mask_arr = core.mergeMask(mask_arr, stride_size + ex_pad)
    
    min_dist = stride_size * 2
    mask_arr = core.rmMaskSingular(mask_arr, stride_size, min_dist)
    
    return  mask_arr,occ_lst     




def semlst2AccCont_helper_findFirstIdx(sem_lst, time_stamp):
    """Find index of the time in occ_hand_lst that > time_stamp """
    for idx in range(len(sem_lst)):
        if timeStampGT(sem_lst[idx][0][0],time_stamp):
            break
    return idx



def semlst2AccCont(sem_lst, data_arr, tag_arr):    
    """Extract find occ data data_arr from occ data from semantic list
        IMPORTANT: first entry in occ hand lst time > ......data arr*****add assert later 
        Args:
            occ_hand_lst (list(list)): lst of occ data read directly from csv file that records
                                    humen labeled data
            data_arr (array(int)): The array of data poitns.
            tag_arr (array(string)): The array of the time stamp for each of the data point.
    
        EXAMPLE:
        tag_arr, data_arr  = convertAccDataFromCSV(data_file)
        occ_hand_lst = readCSV2Lst(occ_handLabeled_file_name)
        data1_lst, data2_lst = occHandLst2AccCont(occ_hand_lst, data_arr, tag_arr)
        for i in range(len(data1_lst)):
            print data_label2[i][1]
            plt.plot(data_label2[i][0])
            plt.show()
    """
    
    data_lst = []

    num_sem = len(sem_lst)
    num_data = data_arr.shape[0]

    idx = semlst2AccCont_helper_findFirstIdx(sem_lst, tag_arr[0])
    pre = 0 
    cur = 0
    while idx < num_sem and pre < num_data:

        start_time = sem_lst[idx][0][0]

        find_start = 0
        while pre < num_data:
            if timeStampGT(start_time, tag_arr[pre]) is False:
                find_start = 1
                break  
            pre = pre + 1 

        if find_start == 1:
            cur = pre
            end_time = sem_lst[idx][0][1]

            find_end = 0 
            while cur < num_data:
                #print 'in while1'
                if timeStampGT(end_time, tag_arr[cur]) is False:
                    find_end = 1
                    break
                cur = cur + 1
                
            if find_end == 1:
                data_lst.append(sem_lst[idx][1])
                pre = cur-1
                
        idx = idx + 1

    data_cont = np.array([])    
    for i in range(len(data_lst)):
        data_cont = np.concatenate((data_cont, data_lst[i]), axis=0)
        
    return data_cont


