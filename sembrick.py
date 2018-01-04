import numpy as np
import matplotlib.pyplot as plt
import copy
import warnings 


import wnfilter as wf
import core
import util




class TimeSeriesSeg(object):
    
    '''This is a base class for time serier data   
    '''
    
    def __init__(self, time_series_data, sensor_name_str):
    
        self._y_arr = time_series_data[1]
        self._t_arr = time_series_data[0]
        
        self._sensor_name = sensor_name_str
        self._msk_lst = []        
        
        self._start_time = time_series_data[0][0]
        self._end_time =  time_series_data[0][-1]

    def __len__(self):
        '''Length of the signal'''
        return self.getYArray().shape[0]
    
    def __gt__(self, ts_seg):
        '''Greater than in chronological order'''
        return self.getStartTime() > ts_seg.getEndTime() 
        
        
    def __lt__():
        '''Less than in chronological order'''
        return self.getEndTime() < ts_seg.getStartTime() 
    
    
    def __eq__(self, ts_seg):
        '''A time series segment S1 equals to another time sereis S2 segment
        when they are from the same sensor and have the same time range
        '''
        return  self.getSensorName() == ts_seg.getSensorName() and \
                self.getStartTime() == ts_seg.getStartTime() and \
                self.getEndTime() == ts_seg.getEndTime()
    
    
    def __str__(self):
        return '<Sensor: '+ self.getSensorName() + \
                ' from ' + self.getStartTime() + ' to ' + self.getEndTime() + '>'
    
    
    def __contains__(self, ts_seg):
        '''A time series segment S1 contains another time sereis S2 segment
        when they are from the same sensor and the time range of S2 are in the
        time range of S1
        '''
        if self.getSensorName() != ts_seg.getSensorName():
            return False
        else:
            if self.getStartTime() < ts_seg.getStartTime() and self.getEndTime() > ts_seg.getEndTime():
                return True
            else:
                return False
    
    
    def generateMask(self, t_itvl_lst, msk_name):
        '''Generate MaskTimeSerersSeg from time interval list

            Parameters
            -----------------------
            t_itvl_lst : list[tuple]
                List of time end points
            msk_name : str

        '''

        msk_Y = core.getTimeOverlayMask(self.getTArray().tolist(), t_itvl_lst)

        assert self.getTArray().shape[0] == msk_Y.shape[0], "Not same length"

        time_series_data = [self.getTArray(), msk_Y]

        msk_tss = MaskTimeSeriesSeg(time_series_data, msk_name)

        return msk_tss

    
    def addMaskByTimeIntervalLst(self, t_itvl_lst, msk_name):
        '''Add mask to the list of MaskTimeSeriesSeg

            Parameters
            -----------------------
            t_itvl_lst : list[tuple]
                List of time end points
            msk_name : str

        '''

        msk_tss = self.generateMask(t_itvl_lst, msk_name)

        k = 0
        for i in range(len(self._msk_lst)):
            if self._msk_lst[i].getSensorName() == msk_name:
                Y_array = np.zeros((self.getTArray().shape[0], ))
                Y_array[(self._msk_lst[i].getYArray() + msk_tss.getYArray() )> 0] = 1
                self._msk_lst[i] = MaskTimeSeriesSeg([self.getTArray(), Y_array], msk_name) 
                k = 1
                break

        if k == 0:
            self._msk_lst.append(msk_tss)



    def addMaskByMaskTimeSeriesSeg(self, msk_tss, msk_name):
        '''Add mask to the list of MaskTimeSeriesSeg

            Parameters
            -----------------------
            t_itvl_lst : list[tuple]
                List of time end points
            msk_name : str

        '''

        t_itvl_lst = msk_tss.convert2TimeIntervalLst()

        msk_tss = self.generateMask(t_itvl_lst, msk_name)

        k = 0
        for i in range(len(self._msk_lst)):
            if self._msk_lst[i].getSensorName() == msk_name:
                Y_array = np.zeros((self.getTArray().shape[0], ))
                Y_array[(self._msk_lst[i].getYArray() + msk_tss.getYArray() )> 0] = 1
                self._msk_lst[i] = MaskTimeSeriesSeg([self.getTArray(), Y_array], msk_name) 
                k = 1
                break

        if k == 0:
            self._msk_lst.append(msk_tss)





    def getSmoothed(self):
        '''Smooth the time series data'''
        pass
    
            
    def applyMaskByName(self):
        '''Apply mask on the time series data to get lists of time series segments'''
        pass
        
            
    def printMaskNames(self):
        '''Print mask names'''
        name_lst = []
        for msk in self._msk_lst:
            name_lst.append(msk.getSensorName())

        print name_lst

    def getSampleRate(self):
        '''Get sample rate of the time series data'''
        ####TODO: Hard coded in, must change 
        warnings.warn("Hard coded in 25hz as sample rate. MUST CHANGE")
        return util.getSampleRate(self.getTArray())


    def getMaskByName(self, name):
        '''Get mask by name'''
        for msk in self._msk_lst:
            if  msk.getSensorName() == name:
                return msk


    def getMaskList(self):
        '''Get mask list'''
        return copy.deepcopy(self._msk_lst)


    def getSensorName(self):
        '''Get the name of the sensor that records the data'''
        return copy.deepcopy(self._sensor_name)
    
    
    def getStartTime(self):
        '''Get start time of the data'''
        return copy.deepcopy(self._start_time)
    
    
    def getEndTime(self):
        '''Get the finish time of the data'''
        return copy.deepcopy(self._end_time)
    
    
    def getYArray(self):
        '''Get the time series recording'''
        return copy.deepcopy(self._y_arr)
    
    
    def getTArray(self):
        '''Get the time stamps'''
        return copy.deepcopy(self._t_arr)
    
    
    def plotY(self):
        '''Plot time series data'''
        plt.plot(self._y_arr)
        plt.title(self._sensor_name)
        plt.xlabel('From time '+self._start_time + ' to '+ self._end_time )
        plt.show()
        
        

class AccelTimeSeriesSeg(TimeSeriesSeg):
    '''A time series data class for data from accel sensor'''
    def __init__(self, time_series_data, sensor_name_str):
        #super().__init__(time_series_data, sensor_name_str)
        super(AccelTimeSeriesSeg, self).__init__(time_series_data, sensor_name_str)
        
        self.variance =  np.var(self.getYArray())
        self.mean = np.mean(self.getYArray())
    
    
    def __getslice__(self, i, j):
        '''Get sliced'''
        return  AccelTimeSeriesSeg( (self.getTArray()[i:j], self.getYArray()[i:j] ), \
                                self.getSensorName)
    
    def applyMaskByName(self, msk_name):
        '''Apply mask on signal to get segments of signal'''
       
        msk_seg = self.getMaskByName(msk_name)
        
        if msk_seg != None:
            
            sem_lst = core.msk2Semlst(msk_seg.getYArray(), self.getYArray(), \
                                      self.getTArray())
            seg_lst = []
            for sem in sem_lst:
                seg_lst.append(AccelTimeSeriesSeg(sem, self.getSensorName()) )
            return seg_lst
        else:
            return None 
        
    def getVariance():
        return self.variance
    
    def getMean():
        return self.mean
    
    
    
    
class MaskTimeSeriesSeg(TimeSeriesSeg):
    '''A time series data class for data from occ sensor'''
    def __init__(self, time_series_data , sensor_name_str):
        super(MaskTimeSeriesSeg, self).__init__(time_series_data, sensor_name_str)

    
    def __add__(self, mts_seg):
        '''Union of masked region from self and mts_seg and project one to self'''
        

        t1_itvl_lst = self.convert2TimeIntervalLst()
        
        t2_itvl_lst = mts_seg.convert2TimeIntervalLst()

        new_itvl_lst = core.mergeTimeIntervalLsts([t1_itvl_lst,t2_itvl_lst])
        
        return self.generateMask( new_itvl_lst, self.getSensorName() )
    
    def invert(self,sensor_name):
        '''Invert the mask'''
        Y_array = np.ones((self.getYArray().shape[0],))-self.getYArray()
        
        T_array = self.getTArray()
      
        
        return MaskTimeSeriesSeg((T_array, Y_array), sensor_name)
    

    def __getslice__(self, i, j):
        '''Get sliced'''
        return  MaskTimeSeriesSeg( (self.getTArray()[i:j], self.getYArray()[i:j] ), \
                self.getSensorName())
    
        
    def applyMaskByName(self, msk_name):
        '''Apply mask on signal to get segments of signal'''
       
        msk_seg = self.getMaskByName(msk_name)
        
        if msk_seg != None:
            
            sem_lst = core.msk2Semlst(msk_seg.getYArray(), self.getYArray(), \
                                      self.getTArray())
            seg_lst = []
            for sem in sem_lst:
                seg_lst.append(MaskTimeSeriesSeg(sem, self.getSensorName()) )
            return seg_lst
        else:
            return None 


    def convert2TimeIntervalLst(self):
        
        sem_lst = core.msk2Semlst(self.getYArray(), self.getYArray(), \
                                      self.getTArray())
        res = []
        for sem in sem_lst:
            res.append((sem[0][0],sem[0][-1]))
        return res

    
    
    def getSmoothed(self):
        '''Smooth the mask.
        '''
        sample_rate = self.getSampleRate()

        gap_size = int(sample_rate/2.0)

        min_dis = 3 * sample_rate

        singular_size = sample_rate

        mask_arr = self.getYArray()

        mask_arr = core.mergeMask(mask_arr, gap_size )
        #mask_arr = core.rmMaskSingular(mask_arr, singular_size, min_dis)

        return MaskTimeSeriesSeg((self.getTArray(),mask_arr), self.getSensorName()) 




        
class StrainTimeSeriesSeg(TimeSeriesSeg):
    '''A time series data class for data from accel sensor'''
    def __init__(self, time_series_data, sensor_name_str):
        super(StrainTimeSeriesSeg, self).__init__(time_series_data, sensor_name_str)
        
    def __getslice__(self, i, j):
        '''Get sliced'''
        return  StrainTimeSeriesSeg( (self.getTArray()[i:j], self.getYArray()[i:j] ), \
                self.getSensorName())
    
    def applyMaskByName(self, msk_name):
        '''Apply mask on signal to get segments of signal'''
       
        msk_seg = self.getMaskByName(msk_name)
        
        if msk_seg != None:
            
            sem_lst = core.msk2Semlst(msk_seg.getYArray(), self.getYArray(), \
                                      self.getTArray())
            seg_lst = []
            for sem in sem_lst:
                seg_lst.append(StrainTimeSeriesSeg(sem, self.getSensorName()) )
            return seg_lst
        else:
            return None 


    def n1Filter(self):
        '''Filter out the outliers'''
        i = 1
        Y_temp = self.getYArray()
        while i < Y_temp.shape[0]-1:
            p_interpolate = (Y_temp[i-1] + Y_temp[i+1])/2.0
            if np.abs(Y_temp[i]-p_interpolate) > 0.01:
                Y_temp[i] = p_interpolate
                #print i
            i = i+1
        time_series_data = (self.getTArray(), Y_temp )
        
        return StrainTimeSeriesSeg(time_series_data, self.getSensorName())
    
     


