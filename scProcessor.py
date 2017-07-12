'''
Created on Jun 26, 2017

@author: Khoa Au
kau@kymetacorp.com
'''



from matplotlib import pyplot as plt
import os
import pandas as pd
import json
from sparms.sparmsPkg.s2p_calculations import S2PDataProcessing as DP
import math
import re
import glob
import numpy
from datetime import datetime
import logging
from LoggingUtil import QtHandler


logger = logging.getLogger(__name__)
handler = QtHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)



class scError(Exception):
    pass
"""
This callable object is capable of generating firstpass summary and sidelobe summary.
For firstpass. This object expects the 3 different directory paths, BroadSide_dyn, Off_Broadside, and S2P path. Usually from the Optimization 
Best dyn
For sideLobe. This object expect 1 scorecard path. Could be any path from the FF Folder that contains scorecards.
This class generally filters the scorecard in a way that only the row with appropriate json bounds (freq,pol) are captured and appended to the 
dataframe.
"""
class ReportGenerator():
    def __init__(self,sPath,sl=None,bs=None,obs=None,s2p=None,nf2ff=None,type=None):
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.print_time =datetime.now().strftime('%Y%m%d%H%M%S')
        self.sidelobe=sl
        self.broadside=bs
        self.offbroadside=obs
        self.nearfieldfarfield=nf2ff
        self.s2p_path = s2p
        self.report_type =type
        self.saveDirectory = sPath
        # As long as one of the paths is not none. That path is used to determine that antenna's build number and serial number
        #declaring dataframe variables
        self.ASN=''
        self.golden = pd.read_csv('reference_data.csv')
        self.s2p_frame = object
        self.csv_frame = object
        self.broadside_frame = object
        self.offbroadside_frame = object
        
     
        
    #this method assumes that the antenna serial number starts with AA. This method will not work otherwise    
    def _getSerialNumber_(self,antenna_path):
        #reads the file directory and grabs the antenna serial number
        if 'AA' in antenna_path:    
            s,e = antenna_path.split('AA')        
            e1 = e.split("\\",1)[0]
            antenna_serial_number = "AA" + e1
        elif 'mTC' in antenna_path:
            s,e = antenna_path.split('mTC')        
            e1 = e.split("\\",1)[0]
            antenna_serial_number = "mTC" + e1
        else:#strange antenna pattern
            logger.debug("new Antenna Serial Number, defaults to unknown")
            antenna_serial_number = 'Unknown'
            
        logger.info("Antenna Serial Number found " + str(antenna_serial_number))
        return antenna_serial_number
        
    """
    This method determines what report it should generate. Firstpass and sidelobe reports are generated differently
    for firstpass report. There are 2 sub-reports including s2p and csv. The master_frame will concatinate these dataframes
    If one of  them is empty. The result will just be the other one.
    """
    
    def generate_csv(self,my_csv_report):
        self.broadside_frame = my_csv_report.process('broadside')
        self.offbroadside_frame = my_csv_report.process('offbroadside')
        csv_frame = pd.concat([self.broadside_frame,self.offbroadside_frame])
        csv_frame= csv_frame.ix[(  (csv_frame['Pattern_LPA']==90.0) & (csv_frame['Pattern_PHI']==0.0) & (csv_frame['Pattern_THETA']==0))   | (  (csv_frame['Pattern_LPA']==0.0) & (csv_frame['Pattern_PHI']==0.0) & (csv_frame['Pattern_THETA']==0.0))  | 
                                (  (csv_frame['Pattern_LPA']==90.0) & (csv_frame['Pattern_PHI']==0.0) & (csv_frame['Pattern_THETA']==60.0))   | (  (csv_frame['Pattern_LPA']==0.0) & (csv_frame['Pattern_PHI']==0.0) & (csv_frame['Pattern_THETA']==60.0))  ]
        csv_frame = csv_frame.reset_index(drop = True) 
        return csv_frame
    def generateReport(self):
        whichpath=""
        if self.report_type == 'firstpass':
            #print 'processing firstpass'
            master_frame = pd.DataFrame()
            csv_report = csvGenerator(sPath= self.saveDirectory,bs_path=self.broadside,obs_path=self.offbroadside,reportType=self.report_type)
            s2p_report = s2pGenerator(sPath= self.saveDirectory,s2p_path=self.s2p_path,nf2ff_path=self.nearfieldfarfield)
            
            if self.s2p_path is "":
                logger.debug("no s2p path indicated, proceed with broadside, off broadside path")
                whichpath = self.broadside
                self.csv_frame = self.generate_csv(csv_report)
                master_frame = self.csv_frame
            elif (self.broadside is "") and (self.offbroadside is ""):
                logger.debug("no broadside,offbroadside path indicated, proceed with s2p path")
                whichpath = self.s2p_path
                self.s2p_frame = s2p_report.generate()
                master_frame = self.s2p_frame
               
            else:
                whichpath =self.s2p_path    
                self.s2p_frame = s2p_report.generate()
                self.csv_frame = self.generate_csv(csv_report)#The csv_Frame is a concatination of the broadside frame and off-broadside frame. I also like to keep these two frames seperate for plotting
                master_frame = pd.concat([self.s2p_frame,self.csv_frame],axis =1)
            #print whichpath            
            header = ['frequency','Gain_dBi','Pattern_LPA','Pattern_PHI','Pattern_THETA','Frequencies (GZ)','Optimized S21 + cal (dBi) LPA90P0T0','Theoretical Directivity','NF2FF']
            self.ASN = self._getSerialNumber_(whichpath)
            master_frame.to_csv(os.path.join(self.saveDirectory,self.ASN+"_Firstpass_Report_"+self.print_time +  '.csv'),columns = header)
   
            
            
        if self.report_type == 'sidelobe':
            #print 'processing sidelobe'
            sl_report = csvGenerator(sPath= self.saveDirectory,sl_path=self.sidelobe,reportType=self.report_type)
            sl_report.generateSideLobe()
            
    def generatePlot(self):
        """
        ******************************************RX Report PLOTs**********************************************************
        """
    
        ax = plt.subplot(2,1,1)
        plt.cla()
        plt.title(self.ASN+ ' RX_DATA')
        plt.xlabel('frequency (Gz)')
        plt.ylabel('Gain')
        if self.s2p_path is not "":    
            rx_frame = self.s2p_frame.ix[(self.s2p_frame['Frequencies (GZ)']<13.0)]
            ax.plot(rx_frame['Frequencies (GZ)'], rx_frame['Optimized S21 + cal (dBi) LPA90P0T0'],label = "Optimized S21 vs Cal")
            ax.plot(rx_frame['Frequencies (GZ)'], rx_frame['Theoretical Directivity'],label = "Theoretical Directivity")
        if self.nearfieldfarfield is not "":
            ax.plot(rx_frame['Frequencies (GZ)'], rx_frame['NF2FF'],'o',label = "NF2FF Directivity")
        if self.broadside is not "":    
            rx_frame_broadside = self.broadside_frame.ix[(self.broadside_frame['frequency']) <13.0]
            ax.plot(rx_frame_broadside['frequency'],rx_frame_broadside['Gain_dBi'], label = "Modfreq Gain(dBi) LPA90P0T0")
        if self.offbroadside is not "":    
            rx_0060 = self.offbroadside_frame.ix[(self.offbroadside_frame['frequency']<13.0) & (self.offbroadside_frame['Pattern_LPA']==0) &  (self.offbroadside_frame['Pattern_PHI']==0)   &(self.offbroadside_frame['Pattern_THETA']==60)  ]
            ax.plot(rx_0060['frequency'],rx_0060['Gain_dBi'],'o',label = 'ModFreq LPA0P0T60')         
            rx_90060 = self.offbroadside_frame.ix[(self.offbroadside_frame['frequency']<13.0) & (self.offbroadside_frame['Pattern_LPA']==90) &  (self.offbroadside_frame['Pattern_PHI']==0)   &(self.offbroadside_frame['Pattern_THETA']==60)]
            ax.plot(rx_90060['frequency'],rx_90060['Gain_dBi'],'o',label = "ModFreq LPA90P0T60")
            rx_000 = self.offbroadside_frame.ix[(self.offbroadside_frame['frequency']<13.0) & (self.offbroadside_frame['Pattern_LPA']==0) &  (self.offbroadside_frame['Pattern_PHI']==0)   &(self.offbroadside_frame['Pattern_THETA']==0)]
            ax.plot(rx_000['frequency'],rx_000['Gain_dBi'],'o',label = "ModFreq LPA0P0T0")
            ax.plot(self.golden['rx_freq'],self.golden['rx_opt_cal'],label = "x3_c9_optimized + cal")
        chartBox = ax.get_position()
        ax.set_position([chartBox.x0,chartBox.y0,0.62,chartBox.height])
        ax.legend(loc="lower left", bbox_to_anchor=[1,0],ncol=1, shadow=True)
        #plt.xticks(numpy.arange(min(rx_frame['Frequencies (GZ)']), max(rx_frame['Frequencies (GZ)'])+0.1,0.1))
        plt.autoscale(enable=True, axis='x', tight=True)
        plt.grid()
        """
        ********************************************TX Report PLOTs*********************************************************
        """
        ax =plt.subplot(2,1,2)
        plt.cla()
        plt.title(self.ASN+ " TX_DATA")
        plt.xlabel('frequency (Gz)')
        plt.ylabel('Gain')
        if self.s2p_path is not "":
            tx_frame = self.s2p_frame.ix[(self.s2p_frame['Frequencies (GZ)'])>13.0]
            ax.plot(tx_frame['Frequencies (GZ)'], tx_frame['Optimized S21 + cal (dBi) LPA90P0T0'],label = "Optimized S21 vs Cal")
            ax.plot(tx_frame['Frequencies (GZ)'], tx_frame['Theoretical Directivity'],label = "Theoretical Directivity")
        if self.nearfieldfarfield is not "":
            ax.plot(tx_frame['Frequencies (GZ)'], tx_frame['NF2FF'],'o',label = "NF2FF Directivity")
        if self.broadside is not "":
            tx_frame_broadside = self.broadside_frame.ix[(self.broadside_frame['frequency']) >13.0]
            ax.plot(tx_frame_broadside['frequency'],tx_frame_broadside['Gain_dBi'], label = "Modfreq Gain(dBi) LPA90P0T0")
        if self.offbroadside is not "":    
            tx_0060 = self.offbroadside_frame.ix[(self.offbroadside_frame['frequency']>13.0) & (self.offbroadside_frame['Pattern_LPA']==0) &  (self.offbroadside_frame['Pattern_PHI']==0)   &(self.offbroadside_frame['Pattern_THETA']==60)  ]
            ax.plot(tx_0060['frequency'],tx_0060['Gain_dBi'],'o',label = 'ModFreq LPA0P0T60')
            tx_90060 = self.offbroadside_frame.ix[(self.offbroadside_frame['frequency']>13.0) & (self.offbroadside_frame['Pattern_LPA']==90) &  (self.offbroadside_frame['Pattern_PHI']==0)   &(self.offbroadside_frame['Pattern_THETA']==60)]
            ax.plot(tx_90060['frequency'],tx_90060['Gain_dBi'],'o',label = "ModFreq LPA90P0T60")
            tx_9000 = self.offbroadside_frame.ix[(self.offbroadside_frame['frequency']>13.0) & (self.offbroadside_frame['Pattern_LPA']==0) &  (self.offbroadside_frame['Pattern_PHI']==0)   &(self.offbroadside_frame['Pattern_THETA']==0)]
            ax.plot(tx_9000['frequency'],tx_9000['Gain_dBi'],'o',label = "ModFreq LPA0P0T0")
            ax.plot(self.golden['tx_freq'],self.golden['tx_opt_cal'],label = "x3_c9_optimized + cal")
        chartBox = ax.get_position()
        ax.set_position([chartBox.x0,chartBox.y0,0.62,chartBox.height]) 
        ax.legend(loc="lower left", bbox_to_anchor=[1,0],ncol=1, shadow=True)
        #plt.xticks(numpy.arange(min(tx_frame['Frequencies (GZ)']), max(tx_frame['Frequencies (GZ)'])+0.1,0.1))
        plt.grid()
        
  
"""
Inherited from report generator. this class calculates theoratical directivy from the list of frequencies,gain + cal based on a cal frequency
dictionary and nf2ff directivity from the NF2FF file
@param s2p_path: A directory where the s2p files are saved
@param nf2ff_path:An optional directory in NF where the NF2FF directivity is calculated  
"""        
class s2pGenerator(ReportGenerator):
    def __init__(self,sPath,s2p_path,nf2ff_path=None):#nf2ff transform directivity can be read from the NF first-pass folder
        ReportGenerator.__init__(self,sPath)
        self.NUM = 4.5479  #4* math.pow(3.14159,2)*math.pow(0.34, 2)- math.pow(0.02,2)
        self.fre = [] # array from frequencies from json
        self.gain_at_freq = [] #array of gains based on the frequencies
        self.directivity = []
        self.nf2ff_directivity_path = nf2ff_path
        self.rx_nf2ff_directivity = 0.0
        self.tx_nf2ff_directivity = 0.0
        self.s2pDirectory = s2p_path
       
        with open('freq_cal_dict.txt') as inFile:
            logger.critical('openning freq_cal_dict')
            self.freq_dictionary = json.load(inFile)
 
    def calculateNF2FF(self):
        #os.chdir(self.nf2ff_directivity_path)
        # get the name of the json at LPA0P0T0 which is only TX data
        for file in glob.glob1(self.nf2ff_directivity_path,"*.json"): #if a file is a RX or TX json then read 
            if ( 'TX' in file):
                my_data = json.load(open(os.path.join(self.nf2ff_directivity_path,file)))
                if ((my_data['TX']['Pattern_LPA'] == 0.0) & (my_data['TX']['Pattern_PHI'] == 0.0)& (my_data['TX']['Pattern_THETA'] == 0.0)):
                    tx_jsonName= file.split('_',1)[0]
            if ('RX' in file):
                my_data = json.load(open(os.path.join(self.nf2ff_directivity_path,file)))
                if ((my_data['RX']['Pattern_LPA'] == 90.0) & (my_data['RX']['Pattern_PHI'] == 0.0)& (my_data['RX']['Pattern_THETA'] == 0.0)):
                    rx_jsonName= file.split('_',1)[0]
        for file in glob.glob1(self.nf2ff_directivity_path,"*.csv"):
            if("NF2FF_Rx" in file):
                nf2ff = pd.read_csv(os.path.join(self.nf2ff_directivity_path,file))
                nf2ff=nf2ff.ix[nf2ff['SN']==rx_jsonName ]
                self.rx_nf2ff_directivity = nf2ff['co']
            if("NF2FF_Tx" in file):
                nf2ff = pd.read_csv(os.path.join(self.nf2ff_directivity_path,file))
                nf2ff=nf2ff.ix[nf2ff['SN']==tx_jsonName ]
                self.tx_nf2ff_directivity = nf2ff['cross']
    def generate(self):
        #print self.nf2ff_directivity_path
        if not self.nf2ff_directivity_path is "":
            self.calculateNF2FF()
        for file in glob.glob1(self.s2pDirectory,'*.s2p'):
            giga_freq = float(self.parseFreq(file))*1e-9
            self.fre.append(giga_freq)
            mys2p = DP(os.path.join(self.s2pDirectory,file))
            for key in self.freq_dictionary:
                if key == self.parseFreq(file):
                    value = float(self.freq_dictionary[key]) + float(mys2p.s21_gain_at_frequency(int(self.parseFreq(file)), return_nearest = False)) 
                    self.gain_at_freq.append(value)
                    #print value
            self.directivity.append(abs(10*math.log10(self.NUM/  math.pow(0.3/giga_freq,2)   )))    
        s2p_frame = pd.DataFrame()
        s2p_frame.insert(0, column = "Frequencies (GZ)", value = self.fre)
        #print self.s2p_frame
        s2p_frame.insert(1, column = "Optimized S21 + cal (dBi) LPA90P0T0", value = self.gain_at_freq)
        s2p_frame.insert(2, column = 'Theoretical Directivity',value = self.directivity)
        #self.s2p_frame = self.s2p_frame.ix[self.s2p_frame['Frequencies (GZ)'] >13.0 ]
        s2p_frame=s2p_frame.reset_index(drop = True)
        if not self.nf2ff_directivity_path is "":#adding nf2ff data if the path is indicated
            logger.debug('Directivity path is given, adding directivity data')
            tx_index=  s2p_frame[s2p_frame['Frequencies (GZ)']==14.0].index.tolist()
            s2p_frame.set_value(tx_index,'NF2FF',float(self.tx_nf2ff_directivity))
            rx_index = s2p_frame[s2p_frame['Frequencies (GZ)']==11.8].index.tolist()
            s2p_frame.set_value(rx_index,'NF2FF',float(self.rx_nf2ff_directivity))
        
        s2p_frame.sort_values(by =['Frequencies (GZ)'], ascending = True, inplace = True)
        s2p_frame=s2p_frame.reset_index(drop=True)
        return s2p_frame
  
    def parseFreq(self,file):
        return ''.join(re.findall('_f=(.*?)_L', file))

"""
**********************************************************************************************************************************
"""
class csvGenerator(ReportGenerator):
    def __init__(self,sPath,reportType,sl_path=None,bs_path=None,obs_path=None):
        ReportGenerator.__init__(self,sPath)
        
        self.ff_broadside_path = bs_path
        self.ff_offbroadside_path = obs_path
        self.ff_sidelobe_path =sl_path
        self.type_of_scan = ''
        self.pattern_freq_rx = 0.0
        self.pattern_lpa_rx = 0
        self.pattern_freq_tx = 0.0
        self.pattern_lpa_tx = 0
        self.process_type = reportType
        
    def process(self,ffType):
        if ffType == 'broadside':
            directory_path = self.ff_broadside_path
            logger.info('processing Broad Side Data')
        elif ffType =='offbroadside':
            directory_path = self.ff_offbroadside_path
            logger.info('Processing off Broadside Data')
        list = []
        if self.process_type == 'sidelobe':
            directory_path = self.ff_sidelobe_path
            logger.info('processing side lobe Data')
            colHeader = ['Theta_deg','phi','xpd','Sidelobe_1_dBc','Sidelobe_1_deg','Sidelobe_2_dBc','Sidelobe_2_deg','pol','frequency']
        elif self.process_type =='firstpass':
            colHeader = ['frequency','Gain_dBi','pol'] #read the appropriate data to save memory         
        #print colHeader
        if (directory_path == ""):
            return
        
        """
        Filter loop for json lpa and frequencies bounds comparing to the scorecard pol and Frequencies. For LPA values. A tolarance of 
        0.5 is applied to the filter.
        """
        try:
            for file in sorted(os.listdir(directory_path)):
                if 'scorecard' in file:
                    #print file
                    df = pd.read_csv(os.path.join(directory_path,file),usecols = colHeader)
                    #print df
                    #if found a score card, check if it is a Tx scorecard or a Rx score card?
                    if ('_Rx_' in file):
                        self.parseRxJson(self.getRxJsonName(file),directory_path)
                        #print df['pol']
                        #print numpy.isclose(df['pol'],self.pattern_lpa_rx,rtol = 0.5)
                        reduced_df = df.ix[(df['frequency']==float(self.pattern_freq_rx)) & (numpy.isclose(df['pol'],float(self.pattern_lpa_rx),atol = 0.5))]
                        reduced_df.insert(0, column = 'Pattern_FREQ_RX', value =self.pattern_freq_rx)
                        reduced_df.insert(0, column = 'Pattern_LPA', value =self.pattern_lpa_rx)
                        reduced_df.insert(0, column = 'Pattern_PHI', value =self.pattern_phi)
                        reduced_df.insert(0, column = 'Pattern_THETA', value =self.pattern_theta)
                        list.append(reduced_df)
                    elif ('_Tx_' in file) :
                        #logger.info(self.current_time + ' Found a Tx scorecard')
                        if ('_RxRef_' in file): #indication of MiniPostOpt Scan
                            self.parseTxJson(self.getTxJsonNameMiniPostOpt(file),directory_path)    
                        else:
                            self.parseTxJson(self.getTxJsonName(file),directory_path)
                        reduced_df = df.ix[(df['frequency']==float(self.pattern_freq_tx)) & (numpy.isclose(df['pol'],float(self.pattern_lpa_tx),atol=0.5)    )]
                        reduced_df.insert(0, column = 'Pattern_FREQ_TX', value =self.pattern_freq_tx)
                        reduced_df.insert(0, column = 'Pattern_LPA', value =self.pattern_lpa_tx)
                        reduced_df.insert(0, column = 'Pattern_PHI', value =self.pattern_phi)
                        reduced_df.insert(0, column = 'Pattern_THETA', value =self.pattern_theta)
                        list.append(reduced_df)
        except:
                raise RuntimeError ("invalid path to scorecard folder")
      
        
        
        
        csv_frame = pd.concat(list)
        csv_frame.sort_values(by =['frequency','pol','Pattern_PHI','Pattern_THETA'], ascending = True, inplace = True)
        csv_frame = csv_frame.reset_index( drop = True)
        return csv_frame     
    def generateSideLobe(self):
        header = ['Pattern_FREQ_RX','Pattern_FREQ_TX','Pattern_LPA','Theta_deg','phi','xpd','Sidelobe_1_dBc','Sidelobe_1_deg','Sidelobe_2_dBc','Sidelobe_2_deg'] 
        self.csv_frame=self.process('sidelobe')
        self.csv_frame.to_csv(os.path.join(self.saveDirectory,self._getSerialNumber_(self.ff_sidelobe_path) + "_Sidelobe_Report_"+self.print_time+".csv"),columns = header)
        return self.csv_frame
    """
    The parse tx/rx methods below reads the value by key in the corresponding json files and
    save those value into appropriate global variables
    @param tx_name:generated/parsed by the method getTx
    @param rx_name:generated/parsed by the method getRx:  
    """    
    def parseTxJson(self,tx_name,csv_path):
        #reiterate through the folder again to find the appropriate tx jason
        #os.chdir(csv_path)
        for file in glob.glob1(csv_path,"*.json"):
                #check for tx name
            if tx_name in file:
                    #read that file
                my_data = json.load(open(os.path.join(csv_path,file)))
                    #print 'tx json freqeuncy values: ' + str(my_data['TX']['Pattern_FREQ'])
                self.pattern_freq_tx = my_data['TX']['Pattern_FREQ']
                self.pattern_lpa_tx = my_data['TX']['Pattern_LPA']
                self.pattern_theta = my_data['TX']['Pattern_THETA']
                self.pattern_phi = my_data['TX']['Pattern_PHI']
                    #print str(self.pattern_freq_tx) + ' , ' +str(self.pattern_lpa_tx)
    def parseRxJson(self,rx_name,csv_path):
        #os.chdir(csv_path)
        for file in glob.glob1(csv_path,"*.json"):
                #check for tx name
            if rx_name in file:
                    #read that file
                my_data = json.load(open(os.path.join(csv_path,file)))
                #print 'tx json freqeuncy values: ' + str(my_data['RX']['Pattern_FREQ'])
                #save the appropriate data 
                self.pattern_freq_rx = my_data['RX']['Pattern_FREQ']
                self.pattern_lpa_rx = my_data['RX']['Pattern_LPA']
                self.pattern_theta = my_data['RX']['Pattern_THETA']
                self.pattern_phi = my_data['RX']['Pattern_PHI']
                
    def getRxJsonName(self,my_scorecard):
        _tx_ = my_scorecard.split('_',2)[1]
        logger.debug("tx json name found " + str(_tx_))
        return _tx_
    def getTxJsonName(self,my_scorecard):
        _rx_ = my_scorecard.split('_',3)[2]
        logger.debug("rx json name found " + str(_rx_))
        
        return _rx_
    def getTxJsonNameMiniPostOpt(self,my_scorecard):
        #logger.debug(self.current_time + ' Tx Minipost Opt Json Name is:' + my_scorecard.split('_',4)[3])
        return my_scorecard.split('_',4)[3]        
if __name__ == "__main__":
    #rg = s2pGenerator(sPath= "C:\dev\Test3\ExportTest" ,s2p_path= "C:\dev\AAE000J170417056 (U7.47R6-01)\Opt\dynBW_1_best",nf2ff_path = "C:\dev\AAE000J170417056 (U7.47R6-01)\NF\RF_First_Pass (Using Jsons from U7.47R6-01)" )
    #print rg.generate()
    
    print "Test" 
    #rgsl = csvGenerator(sPath= "C:\dev\Test3\ExportTest",sl_path="C:\dev\AAE000J170503066 (U7.47R6-11)\RF_DVT_TC1\FF\Scan_Roll_Off_170520",reportType = "sidelobe")
    #rgsl.generateSideLobe()
    #rgff = csvGenerator(sPath= "C:\dev\Test3\ExportTest",bs_path="C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Broadside_DBW",obs_path="C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Off_Broadside",reportType = 'firstpass')
    #rgff = csvGenerator(sPath= "C:\dev\Test3\ExportTest",bs_path="C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Broadside_DBW",obs_path="C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Off_Broadside",reportType = 'firstpass')
    #print rgff.generateCSV()
    #FFDF = pd.concat([rgff.generateCSV(),rg.generate()],axis = 1)
    
    #print FFDF
    #slrp = GENERATE(saveDir="C:\dev\Test3\ExportTest",sl="C:\dev\AAE000J170503066 (U7.47R6-11)\RF_DVT_TC1\FF\Scan_Roll_Off_170520",reportType="sidelobe")
    #slrp.generatereport()
    #my_report = ReportGenerator(sPath="C:\dev\Test3\ExportTest",bs="C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Broadside_DBW",obs="C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Off_Broadside",s2p = 'C:\dev\AAE000J170417056 (U7.47R6-01)\Opt\dynBW_1_best',nf2ff='C:\dev\AAE000J170417056 (U7.47R6-01)\NF\RF_First_Pass (Using Jsons from U7.47R6-01)',type='firstpass')
    #my_report = ReportGenerator(sPath="C:\dev\Test3\ExportTest",bs="C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Broadside_DBW",obs="C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Off_Broadside",s2p = "K:\Public\Engineering\LabData\Ku Radial\Test Data\Ku 70cm\mTennaU7 (5.1 TFT)\mTCLA-170409-01 (Ku70TFT5.1-X2-C0)\Opt\dynBW_1_best",nf2ff='C:\dev\AAE000J170417056 (U7.47R6-01)\NF\RF_First_Pass (Using Jsons from U7.47R6-01)',type='firstpass')
    #my_report.generateReport()
    
    my_reportsl = ReportGenerator(sPath="C:\dev\Test3\ExportTest",sl="C:\dev\AAE000J170503066 (U7.47R6-11)\RF_DVT_TC1\FF\Scan_Roll_Off_170520",type="sidelobe")
    my_reportsl.generateReport()

