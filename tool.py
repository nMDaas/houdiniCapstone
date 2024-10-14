import hou
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtWidgets import QFileDialog, QPushButton
from collections import defaultdict

global filepaths

global numColorGroups
numColorGroups = 0

def printParms(node):
    for p in node.parms():
        print(p)
        print(p.eval())

def loadVexString(filename):
    with open(filename, 'r') as file:
        vex_code_string = file.read()
    return vex_code_string

def addColorCodeGroupsToEdit(self):
    # Add labels and color display frames to the grid layout
    for i in range(4):  # Adjust the range for the number of rows
        label = QtWidgets.QLabel(f"Color {i + 1}")
        color_display_frame = ColorDisplayFrame(self, index=i)  # Custom QFrame

        # Add to grid layout (label on the left, color display frame on the right)
        self.ui.colorGridLayout.addWidget(label, i + 1, 0)
        self.ui.colorGridLayout.addWidget(color_display_frame, i + 1, 1)

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MyWidget,self).__init__()
        ui_file = '/Users/natashadaas/houdiniCapstone/gui.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        
        #connect buttons to functions
        self.ui.select_button.clicked.connect(selectMap)
        self.ui.apply_button.clicked.connect(apply)
        
        addColorCodeGroupsToEdit(self)
 
class ColorDisplayFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, index=0):
        super(ColorDisplayFrame, self).__init__(parent)
        self.index = index
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setStyleSheet("background-color: #eb4034;")  # Default color
        self.setMinimumSize(50, 25)

    # Override mousePressEvent to open a non-modal color picker
    def mousePressEvent(self, event):
        self.open_color_picker()

    def open_color_picker(self):
        # Open color picker dialog (non-modal)
        color_dialog = QtWidgets.QColorDialog(self)  # Ensure it's parented correctly
        color_dialog.setWindowTitle("Select Color")
        color_dialog.setOption(QtWidgets.QColorDialog.DontUseNativeDialog, False)  # Optional, ensures a consistent appearance
        color_dialog.setStyleSheet("") 
        
        color_dialog.show()

        # Handle the accepted signal (non-blocking)
        color_dialog.finished.connect(lambda result: self.handle_color_selection(result, color_dialog))

    def handle_color_selection(self, result, color_dialog):
        if result == QtWidgets.QDialog.Accepted:  # 1 means OK was clicked
            color = color_dialog.currentColor()  # Get the selected color
            if color.isValid():
                # Update the QFrame (color display box) background to the selected color
                self.setStyleSheet(f"background-color: {color.name()};")

        color_dialog.deleteLater()  # Clean up the dialog after use
          
            
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
        
def getAttribMapColors(node):
    node = node.geometry()
    color_attribute = node.pointFloatAttribValues("Cd")
    numCdComponents = 3  # RGB

    # Create a list of color_attribute grouped into RGB colors for each grid cell
    color_tuples = [
        tuple(color_attribute[i:i + numCdComponents])
        for i in range(0, len(color_attribute), numCdComponents)
    ]

    # Dictionary to count occurrences of each scaled color
    color_groups = defaultdict(int)
    
    # Count occurrences of each color after multiplying by 255 and rounding to 0 decimal points
    for color in color_tuples:
        # Multiply by 255 and round to 0 decimal points
        scaled_color = tuple(round(c * 255) for c in color)  
        color_groups[scaled_color] += 1

    # Print scaled colors and their counts
    # Filter for counts >= 20 (this gets the main color codes used in the picture)
    print("\nScaled Color Groups and Counts (Count >= 20):")
    for scaled_color, count in color_groups.items():
        if count >= 20:
            print(f"Scaled Color: {scaled_color}, Count: {count}")
            
    print("\n")
            
    print("\nScaled Color Groups and Counts (Count < 20):")
    for scaled_color, count in color_groups.items():
        if count < 20:
            print(f"Scaled Color: {scaled_color}, Count: {count}")
        
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
    deleteThisPLEASE = "/Users/natashadaas/houdiniCapstone/inputImages/colorGroupingTestImage.jpg"
    hou.parm('/obj/terrain/attribfrommap/filename').set(deleteThisPLEASE)
    hou.parm('/obj/terrain/attribfrommap/uv_invertv').set(1)
    hou.parm('/obj/terrain/attribfrommap/srccolorspace').set("linear")
    n_attribFromMap.setPosition(hou.Vector2(2, 0)) 
    n_attribFromMap.setInput(0, n_terrainGrid)
    #printParms(n_attribFromMap)
    
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
    
    # create heightfield node
    n_heightfield = n_terrain.createNode("heightfield", "heightfield")
    hou.parm('/obj/terrain/heightfield/sizex').set(500)
    hou.parm('/obj/terrain/heightfield/sizey').set(500)
    
    # create heightfield project node
    n_heightfield_project = n_terrain.createNode("heightfield_project", "heightfield_project")
    n_heightfield_project.setInput(0, n_heightfield)
    n_heightfield_project.setInput(1, n_polyextrude_terrain)
    
    # create heightfield blur node
    n_heightfield_blur = n_terrain.createNode("heightfield_blur", "heightfield_blur")
    hou.parm('/obj/terrain/heightfield_blur/radius').set(22)
    n_heightfield_blur.setInput(0, n_heightfield_project)
    
    # create heightfield noise node
    n_heightfield_noise = n_terrain.createNode("heightfield_noise", "heightfield_noise")
    hou.parm('/obj/terrain/heightfield_noise/elementsize').set(275)
    n_heightfield_noise.setInput(0, n_heightfield_blur)
    
    hou.node('/obj/terrain/heightfield_noise').setDisplayFlag(True)
    
    n_terrain.layoutChildren()
    
    getAttribMapColors(n_attribFromMap)
     
    
win = MyWidget()
win.show()