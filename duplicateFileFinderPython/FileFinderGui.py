import FileFinder as FF
from os.path import abspath
from PyQt5 import Qt, QtGui, QtCore

class runThread(QtCore.QThread):
    setMaxProgressSignal = QtCore.pyqtSignal(int)
    setCurrentProgressSignal = QtCore.pyqtSignal(int)

    def __init__(self, ff, paths):
        QtCore.QThread.__init__(self)
        self.ff = ff
        self.paths = paths

    def __del__(self):
        self.wait()

    def setMaxProgress(self, val):
        self.setMaxProgressSignal.emit(val)

    def setCurrentProgress(self, val):
        self.setCurrentProgressSignal.emit(val)

    def run(self):
        self.ff.run(self.paths, [self.setMaxProgress, self.setCurrentProgress])

class FileFinderGui(Qt.QMainWindow):
    """GUI For finding duplicate files"""
        
    def __init__(self):
        super(FileFinderGui, self).__init__()
        self.initUI()
        self.fileFinder = FF.FileFinder()
        
    def initUI(self):
        self.pathList = Qt.QListWidget()

        # Create Main Widgets
        self.createActions()
        self.createMenuBar()
        self.createToolBar()
        self.createStatusBar()

        # Create all connections after initializing
        self.createConnections()
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Dupliate File Finder')
        self.setCentralWidget(self.pathList)

        # Set delete option to false since no paths are set initially
        self.deletePathAct.setEnabled(False)
        
        self.show()

    def openOutputFile(self):
        self.fileFinder.openFile()

    def setOutputFilePath(self):
        file = Qt.QFileDialog.getSaveFileName(self, 'Get Output File Name', filter="HTML File (*.html)")

        if len(file) > 0:
            self.fileFinder.setupOutputFilePath(file[0])

    def addPath(self):
        path = Qt.QFileDialog.getExistingDirectory(self, 'Add Path')
        self.addPathWithPath(path)

    def addPathWithPath(self, path):
        if len(path) > 0:
            path = abspath(path)
            if self.pathList.findItems(path, QtCore.Qt.MatchFixedString) == []:
                self.pathList.addItem(Qt.QListWidgetItem(path))

            if self.pathList.count() > 0:
                self.deletePathAct.setEnabled(True)

    def deletePath(self):
        items = self.pathList.selectedItems() 

        for item in items:
            self.pathList.takeItem(self.pathList.row(item))

        if self.pathList.count() <= 0:
            self.deletePathAct.setEnabled(False)

    def turnDeepScanOn(self):
        self.fileFinder.setDeepScanFlag(True)

    def turnDeepScanOff(self):
        self.fileFinder.setDeepScanFlag(False)

    def setProgressBarMax(self, val):
        self.progressBar.setMaximum(val)

    def updateProgressBar(self, val):
        self.progressBar.setValue(val)

    def run(self):
        paths = []
        self.updateProgressBar(0)
        for i in range(self.pathList.count()):
            paths.append(self.pathList.item(i).text())
        if paths != []:
            self.worker = runThread(self.fileFinder, paths)
            
            self.worker.setMaxProgressSignal.connect(self.setProgressBarMax)
            self.worker.setCurrentProgressSignal.connect(self.updateProgressBar)

            self.worker.start()

    def createConnections(self):
        self.openFileAct.triggered.connect(self.openOutputFile)
        self.setOutputFilePathAct.triggered.connect(self.setOutputFilePath)
        self.addPathAct.triggered.connect(self.addPath)
        self.deletePathAct.triggered.connect(self.deletePath)
        self.deepScanOnAct.triggered.connect(self.turnDeepScanOn)
        self.deepScanOffAct.triggered.connect(self.turnDeepScanOff)
        self.runAct.triggered.connect(self.run)
        self.exitAct.triggered.connect(Qt.qApp.quit)

    def createActions(self):
        self.openFileAct = Qt.QAction("Open File", self)
        self.openFileAct.setShortcut("Ctrl+O")
        self.openFileAct.setStatusTip("Open File")

        self.setOutputFilePathAct = Qt.QAction("Set Output File Path", self)
        self.setOutputFilePathAct.setShortcut("Ctrl+P")
        self.setOutputFilePathAct.setStatusTip("Set Output File Path")

        self.addPathAct = Qt.QAction("Add Path", self)
        self.addPathAct.setShortcut("Ctrl+A")
        self.addPathAct.setStatusTip("Add Path")

        self.deletePathAct = Qt.QAction("Delete Path", self)
        self.deletePathAct.setShortcut("Ctrl+D")
        self.deletePathAct.setStatusTip("Delete Path")

        # Toggle Deep Scan On
        self.deepScanOnAct = Qt.QAction("On", self)
        self.deepScanOnAct.setStatusTip("Turn Deep Scan On")
        self.deepScanOnAct.setCheckable(True)
        # Toggle Deep Scan Off
        self.deepScanOffAct = Qt.QAction("Off", self)
        self.deepScanOffAct.setStatusTip("Turn Deep Scan Off")
        self.deepScanOffAct.setCheckable(True)
        # Toggle Deep Scan On/Off
        self.deepScanGroupAct = Qt.QActionGroup(self)
        self.deepScanGroupAct.addAction(self.deepScanOnAct)
        self.deepScanGroupAct.addAction(self.deepScanOffAct)
        self.deepScanOffAct.setChecked(True)

        self.runAct = Qt.QAction("Run Scan", self)
        self.runAct.setShortcut("Ctrl+R")
        self.runAct.setStatusTip("Run Scan")

        self.exitAct = Qt.QAction("Exit", self)
        self.exitAct.setShortcut("Ctrl+Q")
        self.exitAct.setStatusTip("Exit Application")

    def createMenuBar(self):
        self.menuBar = Qt.QMenuBar()
        
        # File Menu
        self.fileMenu = self.menuBar.addMenu("File")
        self.fileMenu.setStatusTip("Open File Menu")
        self.fileMenu.addAction(self.openFileAct)
        self.fileMenu.addAction(self.setOutputFilePathAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        # Settings Menu
        self.settingsMenu = self.menuBar.addMenu("Settings")
        self.settingsMenu.setStatusTip("Open Settings Menu")

        self.settingsMenu.addAction(self.addPathAct)
        self.settingsMenu.addAction(self.deletePathAct)
        self.settingsMenu.addSeparator()

        self.deepScanMenu = Qt.QMenu("Toogle Deep Scan")
        self.deepScanMenu.setStatusTip("Toggle Deep Scan On/Off")
        self.settingsMenu.addMenu(self.deepScanMenu)
        self.deepScanMenu.addAction(self.deepScanOnAct)
        self.deepScanMenu.addAction(self.deepScanOffAct)
        
        self.setMenuBar(self.menuBar)

    def createToolBar(self):
        self.toolBar = Qt.QToolBar()
        
        self.toolBar.addAction(self.openFileAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.addPathAct)
        self.toolBar.addAction(self.deletePathAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.runAct)

        self.addToolBar(self.toolBar)

    def createStatusBar(self):
        self.sb = Qt.QStatusBar()

        self.progressBar = Qt.QProgressBar()
        self.progressBar.setValue(0)
        self.progressBarFunctions = [self.setProgressBarMax, self.updateProgressBar]
        self.sb.addPermanentWidget(self.progressBar)

        self.setStatusBar(self.sb)