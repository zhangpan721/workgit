import copy
import core
import sepdata as sd
import retrivedata as rd

class LabelDataOutput(object):
    '''This class label the data in DataOutput instance'''
    
    def __init__(self, data_out_put):
        assert isinstance(data_out_put ,DataOutput) == True,\
        'data_out_put must by DataOutput type'
        self.__data_out_put = data_out_put
        
        self.__setMeaningFulTimeIntervalLst( data_out_put.getAccelTimeSeriesSegLst(), \
                                             data_out_put.getAccelSensorNameLst() )
        
        self.__setSinglePersonTimeIntervalLst(data_out_put.getAccelTimeSeriesSegLst()[0], \
                                              self.getMeaningfulTimeIntervalLst())
        

    def __setMeaningFulTimeIntervalLst(self,lst_of_accel_tss,sensor_name_lst):
        '''Set meaningful time interval list given from start_time to end_time'''
    
        lst_of_meaningful_time_interval_lst = []
        
        i = 0
        for sensor_name in sensor_name_lst:
            
            meaningful_time_interval_lst = \
                                sd.createMeaningfulTimeIntervalLstFromAccel(lst_of_accel_tss[i],\
                                                                         filter_type = 'threshold_121')

            lst_of_meaningful_time_interval_lst.append(meaningful_time_interval_lst)
            i = i + 1

        time_interval_lst_all = core.mergeTimeIntervalLsts( lst_of_meaningful_time_interval_lst )

        self.__meanginful_time_interval_lst = time_interval_lst_all
        print 
        print '---------------- Complete setting MeaningFulTimeIntervalLst'

    
    def __setSinglePersonTimeIntervalLst(self, t_tss, meaningful_time_interval_lst):
        '''Get single person time interval list given from start_time to end_time
        '''
        sensor_name = 'test-env-cam-1-occ'

        #occ_cam_single_person_tss = rd.readSinglePersonMaskOccCamFromServer(pier9_bridge_info, \
        #                                                                           sensor_name ,\
        #                                                                           start_time, end_time)

        occ_cam_multy_people_tss = \
                    rd.readMultyPeopleMaskOccCamFromServer\
                                        (self.__data_out_put.getSetInfo(), \
                                           sensor_name ,\
                                           self.__data_out_put.getStartTime(), \
                                           self.__data_out_put.getEndTime())
                
        
        occ_multy_people_time_interval_lst = occ_cam_multy_people_tss.convert2TimeIntervalLst()

        singlePerson_time_interval = sd.createSinglePersonTimeInterval_OccCamMsk_MeaningfulMsk\
                                                        (  t_tss, \
                                                         occ_multy_people_time_interval_lst,\
                                                         meaningful_time_interval_lst)
            

        self.__single_person_time_interval_lst = singlePerson_time_interval
        
        print 
        print '----------------Complete setting SinglePersonTimeIntervalLs'
        
    def getMeaningfulTimeIntervalLst(self):
        '''Get meaningful time interval list from server'''
        return copy.deepcopy(self.__meanginful_time_interval_lst) 
    
    
    def getSinglePersonTimeIntervalLst(self):
        '''Get single person time interval list from server'''
        return copy.deepcopy(self.__single_person_time_interval_lst)
    



class DataOutput(object):
    def __init__(self, start_time, end_time, pier9_bridge_info):
        self.__pier9_bridge_info = pier9_bridge_info
        self.__start_time = start_time
        self.__end_time = end_time
        
        self.__accel_sensor_name_lst = ['pi-pier9-bridge-accel-0-4-a-z-0',
                                           'pi-pier9-bridge-accel-0-4-a-z-1',
                                           'pi-pier9-bridge-accel-0-4-a-z-2',
                                           'pi-pier9-bridge-accel-0-4-a-z-3',
                                           'pi-pier9-bridge-accel-0-4-a-z-4',
                                           'pi-pier9-bridge-accel-5-9-a-z-5',
                                           'pi-pier9-bridge-accel-5-9-a-z-6',
                                           'pi-pier9-bridge-accel-5-9-a-z-7',
                                           'pi-pier9-bridge-accel-5-9-a-z-8',
                                           'pi-pier9-bridge-accel-5-9-a-z-9']
        

        self.__strain_sensor_name_lst = ['pi-pier9-bridge-strain-0-right-s-0',
                                         'pi-pier9-bridge-strain-0-left-s-0',
                                         'pi-pier9-bridge-strain-1-right-s-0',
                                         'pi-pier9-bridge-strain-1-left-s-0',
                                         'pi-pier9-bridge-strain-2-left-s-0',
                                         'pi-pier9-bridge-strain-2-right-s-0']
        '''
        
        self.__accel_sensor_name_lst = [
                                           'pi-pier9-bridge-accel-0-4-a-z-2'
                                         ]
        

        self.__strain_sensor_name_lst = ['pi-pier9-bridge-strain-0-right-s-0'
                                        ]
        '''
        self.__setAccelTimeSeriesSegLst(self.getAccelSensorNameLst())
        
        self.__setStrainTimeSeriesSegLst(self.getStrainSensorNameLst())
        

        
    def __setAccelTimeSeriesSegLst(self,sensor_name_lst):
        '''Get accel data from server'''
      
        lst_of_accel_tss = []
        
        for sensor_name in sensor_name_lst:
            accel_tss = rd.readAccelFromServer(self.__pier9_bridge_info, \
                                                sensor_name ,\
                                               self.getStartTime(), \
                                               self.getEndTime())
            lst_of_accel_tss.append(accel_tss)
            print
            print '----------------Complete getting '+ sensor_name
            
        self.__accel_tss_lst = lst_of_accel_tss
        
    
    def __setStrainTimeSeriesSegLst(self,sensor_name_lst):
        '''Get accel data from server'''
      
 
        lst_of_strain_tss = []
        
        for sensor_name in sensor_name_lst :
            strain_tss = rd.readStrainFromServer(self.__pier9_bridge_info, \
                                                       sensor_name ,\
                                                      self.getStartTime(), \
                                                       self.getEndTime())
            
            lst_of_strain_tss.append(strain_tss)
            
            print 
            print '----------------Complete getting '+ sensor_name
            
        self.__strain_tss_lst = lst_of_strain_tss
        
    
    def getSetInfo(self):
        return copy.deepcopy(self.__pier9_bridge_info)
    
    def getAccelTimeSeriesSegLst(self):
        '''Get list of AccelTimeSeriesSeg from server'''
        return copy.deepcopy(self.__accel_tss_lst)
    
    
    def getStrainTimeSeriesSegLst(self):
        '''Get list of StrainTimeSeriesSeg from server'''
        return copy.deepcopy(self.__strain_tss_lst) 
        
       
    def getStrainSensorNameLst(self):
        '''Get strain gauge sensor name list'''
        return copy.deepcopy(self.__strain_sensor_name_lst)
    
    def getAccelSensorNameLst(self):
        '''Get accel sensor name list'''
        return copy.deepcopy(self.__accel_sensor_name_lst)

    def getStartTime(self):
        '''Get the finish time of the data'''
        return copy.deepcopy(self.__start_time)
    
    def getEndTime(self):
        '''Get the finish time of the data'''
        return copy.deepcopy(self.__end_time)
    
