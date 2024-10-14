import hou
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtWidgets import QFileDialog

global filepaths

def loadVexString(filename):
    with open(filename, 'r') as file:
        vex_code_string = file.read()
    return vex_code_string


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
    initial_directory = "/Users/natashadaas/houdiniCapstone"  # Replace this with the desired initial directory
    dialog = QFileDialog()
    dialog.setOption(QFileDialog.DontUseNativeDialog, True)
    dialog.setFileMode(QFileDialog.ExistingFiles)
    dialog.setDirectory(initial_directory)
    dialog.setWindowTitle("Select Folder")
    
    global filepaths
    
    # Open the dialog in a blocking way (modal)
    if dialog.exec_() == QFileDialog.Accepted:
        filepaths = dialog.selectedFiles()
        print("filename: " + filepaths[0])
    else:
        print("No folder selected")           
    
def apply():

    # create terrain Geometry node
    OBJ = hou.node('/obj/')
    n_terrain = OBJ.createNode('geo', 'terrain')
        
    # create grid node in terrain node
    n_terrainGrid = n_terrain.createNode('grid', 'terrainGrid')
    hou.parm('/obj/terrain/terrainGrid/sizex').set(500)
    hou.parm('/obj/terrain/terrainGrid/sizey').set(500)
    hou.parm('/obj/terrain/terrainGrid/rows').set(150)
    hou.parm('/obj/terrain/terrainGrid/cols').set(150)
    
    # create attribute from parameter node
    n_attribFromMap = n_terrain.createNode('attribfrommap', 'attribfrommap')
    global filepaths
    hou.parm('/obj/terrain/attribfrommap/filename').set(filepaths[0])
    hou.parm('/obj/terrain/attribfrommap/uv_invertv').set(1)
    n_attribFromMap.setInput(0, n_terrainGrid)
    
    # create attribute wrangle node
    n_attrib_wrangle = n_terrain.createNode('attribwrangle', 'attribwrangle')
    for p in n_attrib_wrangle.parms():
        print(p)
        print(p.eval())
    hou.parm('/obj/terrain/attribwrangle/class').set(1)
    terrainAttribWrangleVEXpression = loadVexString('/Users/natashadaas/houdiniCapstone/terrainAttribWrangleVEXpression.txt')
    hou.parm('/obj/terrain/attribwrangle/snippet').set(terrainAttribWrangleVEXpression)
    #for n in n_attrib_wrangle.parms():
        #print(n)
     
    hou.node('/obj/terrain/attribfrommap').setDisplayFlag(True)
     
    
win = MyWidget()
win.show()