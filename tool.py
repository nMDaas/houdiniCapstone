import hou
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtWidgets import QFileDialog

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MyWidget,self).__init__()
        ui_file = '/Users/natashadaas/houdiniCapstone/gui.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        
        #connect buttons to functions
        self.ui.select_button.clicked.connect(selectMap)
        self.ui.apply_button.clicked.connect(apply)
        
def selectMap():
    print("hello!")
    initial_directory = "/Users/natashadaas/houdiniCapstone"  # Replace this with the desired initial directory
    dialog = QFileDialog()
    dialog.setOption(QFileDialog.DontUseNativeDialog, True)
    dialog.setFileMode(QFileDialog.ExistingFiles)
    dialog.setDirectory(initial_directory)
    dialog.setWindowTitle("Select Folder")
    
    global file_path
    
    # Open the dialog in a blocking way (modal)
    if dialog.exec_() == QFileDialog.Accepted:
        filepaths = dialog.selectedFiles()
        print("filename: " + filepaths[0])
    else:
        print("No folder selected")           
    
    global folder_path
    
def apply():

    # create terrain Geometry node
    OBJ = hou.node('/obj/')
    terrainGeometry = OBJ.createNode('geo')
    terrainGeometry.setName('terrain', unique_name=True)
        
    # create grid node in terrain node
    TERRAIN = hou.node('/obj/terrain')
    terrainGrid = TERRAIN.createNode('grid')
    
win = MyWidget()
win.show()