import hou
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtWidgets import QFileDialog

global filepaths

def printParms(node):
    for p in node.parms():
        print(p)
        print(p.eval())

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
    n_terrainGrid.setPosition(hou.Vector2(0, 0))  
    
    # create attribute from parameter node
    n_attribFromMap = n_terrain.createNode('attribfrommap', 'attribfrommap')
    global filepaths
    deleteThisPLEASE = "/Users/natashadaas/houdiniCapstone/inputImages/imageNoLand.jpg"
    hou.parm('/obj/terrain/attribfrommap/filename').set(deleteThisPLEASE)
    hou.parm('/obj/terrain/attribfrommap/uv_invertv').set(1)
    n_attribFromMap.setPosition(hou.Vector2(2, 0)) 
    n_attribFromMap.setInput(0, n_terrainGrid)
    
    # create attribute promote node
    n_attrib_promote = n_terrain.createNode("attribpromote", "attribpromote")
    hou.parm('/obj/terrain/attribpromote/inname').set("Cd")
    hou.parm('/obj/terrain/attribpromote/outclass').set(1)
    hou.parm('/obj/terrain/attribpromote/deletein').set(0)
    n_attrib_promote.setPosition(hou.Vector2(4, 0)) 
    n_attrib_promote.setInput(0, n_attribFromMap)
    
    
    # create attribute wrangle node
    n_attrib_wrangle = n_terrain.createNode('attribwrangle', 'attribwrangle')
    hou.parm('/obj/terrain/attribwrangle/class').set(1)
    terrainAttribWrangleVEXpression = loadVexString('/Users/natashadaas/houdiniCapstone/terrainAttribWrangleVEXpression.txt')
    hou.parm('/obj/terrain/attribwrangle/snippet').set(terrainAttribWrangleVEXpression)
    n_attrib_promote.setPosition(hou.Vector2(6, 0)) 
    n_attrib_wrangle.setInput(0, n_attrib_promote)

    # create polyextrude node
    n_polyextrude_terrain = n_terrain.createNode("polyextrude", "polyextrude")
    hou.parm('/obj/terrain/polyextrude/splittype').set(0)
    hou.parm('/obj/terrain/polyextrude/dist').set(1.0)
    hou.parm('/obj/terrain/polyextrude/outputback').set(1)
    hou.parm('/obj/terrain/polyextrude/uselocalzscaleattrib').set(1)
    hou.parm('/obj/terrain/polyextrude/localzscaleattrib').set("zextrusion")
    n_polyextrude_terrain.setPosition(hou.Vector2(8, 0)) 
    n_polyextrude_terrain.setInput(0, n_attrib_wrangle)
    printParms(n_polyextrude_terrain)
    
    hou.node('/obj/terrain/attribwrangle').setDisplayFlag(True)
    
    n_terrain.layoutChildren()
     
    
win = MyWidget()
win.show()