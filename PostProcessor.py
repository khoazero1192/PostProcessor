# -*- coding: utf-8 -*-
from PyQt4.QtCore import QTimer

# Form implementation generated from reading ui file 'reportGen.ui'
#
# Created: Mon Jun 26 11:53:53 2017
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!



"""
@author: Khoa Au
kau@kymetacorp.com

note: according to this ticket: https://github.com/pyinstaller/pyinstaller/issues/1942
the line PyQt4 import Qt cause pyinstaller to hang. Therefore, any method associated with PyQt4 import Qt
has been disabled
"""


from PyQt4 import QtCore, QtGui
import wx
from LoggingUtil import XStream
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from datetime import datetime
import matplotlib.pyplot as plt
from scProcessor import ReportGenerator,logger
from PyQt4.QtCore import QTimer

import os
import time

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

#serpate thread ready for the main thread. So that the console thread runs on a seperate thread. 
#This allows the console to be updated. Original code by hsamba

class Worker(QtCore.QThread):
    def __init__(self, parent = None):
        super(Worker, self).__init__(parent)
        
    def run(self):
        self.emit(QtCore.SIGNAL("threadStart"))
               

class Ui_Form(object):
    ff_sidelobe_path = ''
    def setupUi(self, Form):
        app = wx.App(False)
        w, h = wx.GetDisplaySize()
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #self.current_time = QDateTime.currentDateTime()
        #self.print_time =datetime.now().strftime('%Y%m%d%H%M%S')
        print w,h

        self.popupWin = QtGui.QMessageBox(Form)
        self.popupWin.setWindowTitle('Warning')

        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(w-50,h-100)
        self.tab2 = QtGui.QTabWidget(Form)
        self.tab2.setGeometry(QtCore.QRect(20, 20, w-70,h-140))
        self.tab2.setObjectName(_fromUtf8("tab2"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayoutWidget = QtGui.QWidget(self.tab)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, h/8, w/4.5,h/10))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        
        self.SaveDirButt = QtGui.QPushButton(self.verticalLayoutWidget)
        self.SaveDirButt.setObjectName(_fromUtf8("SaveDirButt"))
        self.verticalLayout.addWidget(self.SaveDirButt)
        self.SaveDirTE = QtGui.QTextEdit(self.verticalLayoutWidget)
        self.SaveDirTE.setObjectName(_fromUtf8("SaveDirTE"))
        self.verticalLayout.addWidget(self.SaveDirTE)
        self.formLayoutWidget = QtGui.QWidget(self.tab)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10,h/4,w/4.5,h/5))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        
        self.SidelobeDirButt = QtGui.QPushButton(self.formLayoutWidget)
        self.SidelobeDirButt.setObjectName(_fromUtf8("SidelobeDirButt"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.SidelobeDirButt)
        self.FirstpassS2PButt = QtGui.QPushButton(self.formLayoutWidget)
        self.FirstpassS2PButt.setObjectName(_fromUtf8("FirstpassS2PButt"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.FirstpassS2PButt)
        self.FirstpassBroadsideButt = QtGui.QPushButton(self.formLayoutWidget)
        self.FirstpassBroadsideButt.setObjectName(_fromUtf8("FirstpassBroadsideButt"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.FirstpassBroadsideButt)
        self.SideLobeTE = QtGui.QTextEdit(self.formLayoutWidget)
        self.SideLobeTE.setObjectName(_fromUtf8("SideLobeTE"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.SideLobeTE)
        self.FirstpassS2PTE = QtGui.QTextEdit(self.formLayoutWidget)
        self.FirstpassS2PTE.setObjectName(_fromUtf8("FirstpassS2PTE"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.FirstpassS2PTE)
        self.FirstpassSCVTE = QtGui.QTextEdit(self.formLayoutWidget)
        self.FirstpassSCVTE.setObjectName(_fromUtf8("FirstpassSCVTE"))
        self.FirstpassOffBroadsideButt = QtGui.QPushButton(self.formLayoutWidget)
        self.FirstpassOffBroadsideTE = QtGui.QTextEdit(self.formLayoutWidget)
        self.formLayout.setWidget(4,QtGui.QFormLayout.LabelRole,self.FirstpassOffBroadsideButt)
        self.formLayout.setWidget(4,QtGui.QFormLayout.FieldRole,self.FirstpassOffBroadsideTE)
        
        self.nf2ffTE=QtGui.QTextEdit()
        self.nf2ffButton = QtGui.QPushButton()
        self.nf2ffButton.setText("NF2FF")
        self.formLayout.setWidget(2,QtGui.QFormLayout.LabelRole,self.nf2ffButton)
        self.formLayout.setWidget(2,QtGui.QFormLayout.FieldRole,self.nf2ffTE)
        
        
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.FirstpassSCVTE)
        self.horizontalLayoutWidget = QtGui.QWidget(self.tab)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, h/2.2, w/4.5, h/7))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        
        self.processFFButt = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.processFFButt.setObjectName(_fromUtf8("processFFButt"))
        self.horizontalLayout.addWidget(self.processFFButt)
        self.ProcessSidelobeButt = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.ProcessSidelobeButt.setObjectName(_fromUtf8("ProcessSidelobeButt"))
        self.horizontalLayout.addWidget(self.ProcessSidelobeButt)
        self.processFFButt.setEnabled(0)
        
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.tab)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(w/4, 50, w/1.47, h/1.4))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))

        """
        Default the mode to firstpass mode
        """
        self.ffCheckBox = QtGui.QRadioButton()
        self.ffCheckBox.setText('First Pass')
        self.ffCheckBox.setChecked(1)
        self.ProcessSidelobeButt.setDisabled(1)
        self.SidelobeDirButt.setDisabled(1)
        self.SideLobeTE.setDisabled(1)
        
        
        self.slCheckBox = QtGui.QRadioButton()
        self.slCheckBox.setText('Side Lobe')
        
        self.ffCheckBox.toggled.connect(self.checkFF)
        self.ffCheckBox.toggled.connect(self.checkSL)
        
        self.checkButtonLayoutWidget = QtGui.QWidget(self.tab)
        self.checkButtonLayoutWidget.setGeometry(QtCore.QRect(20,0,w/5,100))
        
        self.checkButtonLayout = QtGui.QHBoxLayout(self.checkButtonLayoutWidget)
        self.checkButtonLayout.addWidget(self.ffCheckBox)
        self.checkButtonLayout.addWidget(self.slCheckBox)
        
        self._console = QtGui.QTextBrowser()   
        XStream.stdout().messageWritten.connect( self._console.append )
        XStream.stderr().messageWritten.connect( self._console.append ) 
        
        
        logger.info(self.current_time+" First Pass Mode activated")
        
        self.tab2.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tab2.addTab(self.tab_2, _fromUtf8(""))
        
        self.verticalLayoutWidget_3 = QtGui.QWidget(self.tab)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(10,h/1.8, w/4.5, h/5))
        self.verticalLayoutWidget_3.setObjectName(_fromUtf8("verticalLayoutWidget_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbarLayoutWiget = QtGui.QWidget(self.tab)
        self.toolbarLayoutWiget.setGeometry(QtCore.QRect(w/4,20,w/5,h/8))
        self.toolbar = NavigationToolbar(self.canvas,self.toolbarLayoutWiget)
        
        
        #tab 2 section for table of sidelobes data
        self.verticalLayout_3.addWidget(self._console)
        self.verticalLayout_2.addWidget(self.canvas)
        self.retranslateUi(Form)
        self.tab2.setCurrentIndex(0)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._timer)
        self.timer.start(100)
        
        QtCore.QMetaObject.connectSlotsByName(Form)
        QtCore.QObject.connect(self.SaveDirButt,QtCore.SIGNAL(_fromUtf8("clicked()")),self.openDir)
        QtCore.QObject.connect(self.SidelobeDirButt,QtCore.SIGNAL(_fromUtf8("clicked()")),self.openSidelobeDir)
        QtCore.QObject.connect(self.FirstpassBroadsideButt,QtCore.SIGNAL(_fromUtf8("clicked()")),self.openFirstpass_broadside)
        QtCore.QObject.connect(self.FirstpassS2PButt,QtCore.SIGNAL(_fromUtf8("clicked()")),self.openFirstpassS2P)
        #QtCore.QObject.connect(self.processFFButt,QtCore.SIGNAL(_fromUtf8("clicked()")),self.processFirstpass)
        #QtCore.QObject.connect(self.ProcessSidelobeButt,QtCore.SIGNAL(_fromUtf8("clicked()")),self.processSideLobe)
        QtCore.QObject.connect(self.FirstpassOffBroadsideButt,QtCore.SIGNAL(_fromUtf8("clicked()")),self.openFirstpass_offbroadside)
        QtCore.QObject.connect(self.nf2ffButton,QtCore.SIGNAL(_fromUtf8("clicked()")),self.openNF2FF)
        
        
    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Post Process", None))
        self.SaveDirButt.setText(_translate("Form", "Save Directory", None))
        self.SidelobeDirButt.setText(_translate("Form", "Sidelobe Dir", None))
        self.FirstpassS2PButt.setText(_translate("Form", "Optimization s2p", None))
        self.FirstpassBroadsideButt.setText(_translate("Form", "Firstpass Broadside", None))
        self.FirstpassOffBroadsideButt.setText(_translate("Form", 'Firstpass OffBroad', None))
        self.processFFButt.setText(_translate("Form", "Process First Pass", None))
        self.ProcessSidelobeButt.setText(_translate("Form", "Process Sidelobe", None))
        self.tab2.setTabText(self.tab2.indexOf(self.tab), _translate("Form", "Report Generator", None))
        self.tab2.setTabText(self.tab2.indexOf(self.tab_2), _translate("Form", "", None))
        # 2 threads for side lobe and first pass main method
        self.ffbee = Worker()
        QtCore.QObject.connect(self.ffbee,QtCore.SIGNAL("threadStart"),self.processFirstpass,QtCore.Qt.DirectConnection)
        QtCore.QObject.connect(self.processFFButt,QtCore.SIGNAL(_fromUtf8("clicked()")),self.ffbee.start)
        #disable the process button when the thread is started to prevent overwriting 
        self.ffbee.finished.connect(self._restoreUi)
        
        self.slbee = Worker()
        QtCore.QObject.connect(self.slbee,QtCore.SIGNAL("threadStart"),self.processSideLobe,QtCore.Qt.DirectConnection)
        QtCore.QObject.connect(self.ProcessSidelobeButt,QtCore.SIGNAL(_fromUtf8("clicked()")),self.slbee.start)
        self.slbee.finished.connect(self._restoreUi)
       
    
    def _timer(self): # a seperate thread to check for time and test conditions
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if (((str(self.FirstpassS2PTE.toPlainText()) == "")  &  (str(self.FirstpassOffBroadsideTE.toPlainText()) == "") 
                                    &  (str(self.FirstpassSCVTE.toPlainText()) == "")) | self.slCheckBox.isChecked()  ) :
            self.processFFButt.setEnabled(0)
        else:
            self.processFFButt.setEnabled(1)
        
        if (str(self.SideLobeTE.toPlainText()) == "") | (self.ffCheckBox.isChecked()):
            self.ProcessSidelobeButt.setEnabled(0)
        else:
            self.ProcessSidelobeButt.setEnabled(1)
        
    def _restoreUi(self):
        
        logger.info(str(self.current_time) + " COMPLETED")
        
    
    def checkFF(self):
        if self.ffCheckBox.isChecked():
            logger.info(" First Pass Generator Selected")
            self.processFFButt.setEnabled(1)
            self.ProcessSidelobeButt.setDisabled(1)
            self.SidelobeDirButt.setDisabled(1)
            self.SideLobeTE.setDisabled(1)
            self.FirstpassBroadsideButt.setDisabled(0)
            self.FirstpassS2PButt.setDisabled(0)
            self.FirstpassS2PTE.setDisabled(0)
            self.FirstpassSCVTE.setDisabled(0)
            self.FirstpassOffBroadsideButt.setDisabled(0)
            self.FirstpassOffBroadsideTE.setDisabled(0)
            self.nf2ffTE.setDisabled(0)
            self.nf2ffButton.setDisabled(0)
        
    def checkSL(self):
        if self.slCheckBox.isChecked():
            logger.info(" Side Lobe generator Selected")
            self.processFFButt.setDisabled(1)
            self.ProcessSidelobeButt.setEnabled(1)
            self.SidelobeDirButt.setDisabled(0)
            self.SideLobeTE.setDisabled(0)
            self.FirstpassBroadsideButt.setDisabled(1)
            self.FirstpassS2PButt.setDisabled(1)
            self.FirstpassS2PTE.setDisabled(1)
            self.FirstpassSCVTE.setDisabled(1)
            self.FirstpassOffBroadsideButt.setDisabled(1)
            self.FirstpassOffBroadsideTE.setDisabled(1)
            self.nf2ffTE.setDisabled(1)
            self.nf2ffButton.setDisabled(1)
            
    def openNF2FF(self):
        #self.nf2ffTE.setText("C:\dev\AAE000J170417056 (U7.47R6-01)\NF\RF_First_Pass (Using Jsons from U7.47R6-01)")
        self.nf2ffTE.setText(str(QtGui.QFileDialog.getExistingDirectory(None,"Select Directory")))
        logger.info(self.current_time+' opened a NF2FF Transform directory' )
        
        
    def openDir(self):
        #self.SaveDirTE.setText('C:\dev\Test3\ExportTest')
        self.ff_sidelobe_path = str(QtGui.QFileDialog.getExistingDirectory(None, "Select Directory"))
        self.SaveDirTE.setText(self.ff_sidelobe_path)
        logger.info(self.current_time + ' opened a directory')
        
    def openSidelobeDir(self):
        #self.SideLobeTE.setText('C:\dev\AAE000J170503066 (U7.47R6-11)\RF_DVT_TC1\FF\Scan_Roll_Off_170520')
        self.ff_sidelobe_path = str(QtGui.QFileDialog.getExistingDirectory(None, "Select Directory"))
        self.SideLobeTE.setText(self.ff_sidelobe_path)
        logger.info(self.current_time + ' opened a sidelobe directory')
        
    def openFirstpass_broadside(self):
        #self.FirstpassSCVTE.setText('C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Broadside_DBW')
        self.ff_sidelobe_path = str(QtGui.QFileDialog.getExistingDirectory(None, "Select Directory"))
        self.FirstpassSCVTE.setText(self.ff_sidelobe_path)
        logger.info(self.current_time+ ' opened a firstpass broadside folder')
    def openFirstpassS2P(self):
        #self.FirstpassS2PTE.setText('C:\dev\AAE000J170417056 (U7.47R6-01)\Opt\dynBW_1_best')
        self.ff_sidelobe_path = str(QtGui.QFileDialog.getExistingDirectory(None, "Select Directory"))
        self.FirstpassS2PTE.setText(self.ff_sidelobe_path)
        logger.info(self.current_time +   ' opend a firstpass s2p directory')
    def openFirstpass_offbroadside(self):
        #self.FirstpassOffBroadsideTE.setText('C:\dev\AAE000J170417056 (U7.47R6-01)\FF\RF_First_Pass\Off_Broadside')
        self.ff_sidelobe_path = str(QtGui.QFileDialog.getExistingDirectory(None, "Select Directory"))
        self.FirstpassOffBroadsideTE.setText(self.ff_sidelobe_path)
        logger.info( self.current_time +  ' opened a firstpass offbroadside foler')
        
    def processFirstpass(self):
        try:
            my_report = ReportGenerator(sPath=str(self.SaveDirTE.toPlainText()),bs= str(self.FirstpassSCVTE.toPlainText()),obs= str(self.FirstpassOffBroadsideTE.toPlainText()),s2p =str(self.FirstpassS2PTE.toPlainText()),nf2ff=str(self.nf2ffTE.toPlainText()),type='firstpass')
            logger.info(self.current_time+ " Processing first-pass data")
            my_report.generateReport()
            logger.info(self.current_time + " Generating plots based on data")
            my_report.generatePlot()
            logger.info(self.current_time+ ' First pass report succesfully generated and saved at ' + str(self.SaveDirTE.toPlainText()))
            self.canvas.draw()
            #print os.path.join(str(self.SaveDirTE.toPlainText()),'test.png')
            plt.savefig(os.path.join(str(self.SaveDirTE.toPlainText()),str(my_report.ASN)+"_firstpass_report.png"))
        except:
            logger.exception("error in calling processFirstpass")
            
    def processSideLobe(self):    
        try:
            my_reportsl = ReportGenerator(sPath=str(self.SaveDirTE.toPlainText()),sl=str(self.SideLobeTE.toPlainText()),type="sidelobe")
            logger.info(self.current_time+ " Processing sidelobe data")
            my_reportsl.generateReport()
            logger.info(self.current_time+ " Processing side-lobe data")
            logger.info(self.current_time+" Side Lobe report sucessfully generated and saved at  " + str(self.SaveDirTE.toPlainText()))
        except:
            logger.exception("error in calling processSidelobe")
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

