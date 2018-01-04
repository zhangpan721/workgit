import numpy as np

def timeParser(time_str):
    """Parse a string of time format 2017-04-27T02:39:58.457Z in data360"""
    date = time_str.split('T')[0]
    time = time_str.split('T')[1]
    time_large  = time.split('.')[0]
    ms = time.split('.')[1].split('Z')[0]
    
    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]
    
    h = time_large.split(':')[0]
    m = time_large.split(':')[1]
    s = time_large.split(':')[2]
    
    time_dict = {"year":year, "month":month,"day":day,\
                 "hour":h,"minute":m,"second":s,"msecond":ms}
    return time_dict


def timeStampGT(time_greater, time):
    """time_greater > time return true
        inputs are in data360 time stamp format"""
    tg_dict = timeParser(time_greater)
    t_dict = timeParser(time)
    
    tg_int = int(tg_dict["year"]+tg_dict["month"]+tg_dict["day"]+\
                tg_dict["hour"]+tg_dict["minute"]+tg_dict["second"]+tg_dict["msecond"])
    
    t_int = int(t_dict["year"]+t_dict["month"]+t_dict["day"]+\
                t_dict["hour"]+t_dict["minute"]+t_dict["second"]+t_dict["msecond"])
    
    if tg_int > t_int:
        return True
    else:
        return False


	getSampleRate(t_arr)




def getSampleRate(t_arr):
    '''Get sample rate

    
    num_of_points = 1*24 *60 *60 
    
    
    while i < t_arr.shapenum_of_points:
        
    
    t_start = timeParser(t_arr[0])
    d = int(t_start['day'])
    h = int(t_start['hour'])
    m = int(t_start['minute']) 
    s = int(t_start['second'])
    ms = int(t_start['msecond']) 
    ms_end = (((d*24 +  h)*60 + m)*60 + s)* 1000 + ms
    
    
    t_end = timeParser(t_arr[10000])
    d = int(t_end['day'])
    h = int(t_end['hour'])
    m = int(t_end['minute']) 
    s = int(t_end['second'])
    ms = int(t_end['msecond']) 
    ms_end = (((d*24 +  h)*60 + m)*60 + s)* 1000 + ms
    
    assert ms_start > ms_end
    
    ms_end - ms_end/ 
    '''
    ######To do:
    
    return 25
    



