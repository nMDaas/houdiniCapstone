import hou
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtWidgets import QFileDialog
from collections import defaultdict

global initial_directory
initial_directory = "/Users/natashadaas/houdiniCapstone/inputImages/"

global filepaths
filepaths = []

global n_attribFromMap

global hexColorCodeGroups 
hexColorCodeGroups = []

global color_tuples
color_tuples = []

def printParms(node):
    for p in node.parms():
        print(p)
        print(p.eval())

def loadVexString(filename):
    with open(filename, 'r') as file:
        vex_code_string = file.read()
    return vex_code_string

def printHexColors():
    for i in range(len(hexColorCodeGroups)):
        print(f"{i}: {hexColorCodeGroups[i]}")

def rgb_to_hex(rgb_tuple):
    # get r, g and b values in 0-255 range from rgb_tuple
    r, g, b = [int(c) for c in rgb_tuple]
    return f'#{r:02X}{g:02X}{b:02X}'

def hexToRGB(hex_color):
    """Convert a hex color string to an RGB tuple."""
    print("hex_color: ", hex_color)
    hex_color = hex_color.lstrip('#')  # Remove '#' if present
    # Check that the length of the hex color is valid
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    else:
        raise ValueError("Invalid hex color format: must be a 6-digit hex string.")

def addHexColorCodeGroupsToGUI(self):
    # Add labels and color display frames to the grid layout
    for i in range(len(hexColorCodeGroups)):  # Adjust the range for the number of rows
        label = QtWidgets.QLabel(f"Color {i + 1}")
        color_display_frame = ColorDisplayFrame(self, index=i, frameColor=hexColorCodeGroups[i])  # Custom QFrame

        # Add to grid layout (label on the left, color display frame on the right)
        self.ui.colorGridLayout.addWidget(label, i + 1, 0)
        self.ui.colorGridLayout.addWidget(color_display_frame, i + 1, 1)

def updateAttribMapColors():
    print("update")

def updatePythonScript(oldColor, newColor):
    file_path = '/Users/natashadaas/houdiniCapstone/helperScripts/pythonScript.txt'

    # add inputs
    inputs = """    # inputs
oldColorHex = f'{oldColor}'
newColorHex = f'{newColor}'
"""

    # extract geo
    extractGeo = """ # extract geo 
node = hou.pwd()
geo = node.geometry()
color_attribute = list(geo.pointFloatAttribValues("Cd"))
"""

    # base code
    baseCode = """ #Add code to modify contents of geo
For i in range(len(color_attribute)):
	float r = color_attribute[i]
	float g = color_attribute[i+1]
	float b = color_attribute[i+2]

	float r255 = round(r * 255)
	float g255 = round(g * 255)
	float b255 = round(b * 255)

	hex = f'#{r:02X}{g:02X}{b:02X}'

	i++
	i++
	i++
	if (true) {
		# do nothing
	}
"""

    # continue adding else ifs

    # Read the existing content of the file
    with open(file_path, 'r') as file:
        content = file.readlines()
    
    # Check if there are enough lines to modify
    if not content:
        print("The file is empty.")
        return

    # Remove the last line from the content
    last_line = content.pop()  # Remove the last line

    # Append the new else if code
    content.append(new_code)

    # Re-add the last line back
    content.append(last_line)

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.writelines(content)

    print(f"Appended 'else if' statement to {file_path} and re-added the last line.")

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        ui_file = '/Users/natashadaas/houdiniCapstone/gui.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        
        # Connect buttons to functions
        self.ui.select_button.clicked.connect(selectMap)
        self.ui.apply_button.clicked.connect(self.apply)
        self.ui.update_attrib_map_colors_button.clicked.connect(updateAttribMapColors)

    def apply(self):
        # Create terrain Geometry node
        OBJ = hou.node('/obj/')
        n_terrain = OBJ.createNode('geo', 'terrain')
        
        # Create grid node in terrain node
        n_terrainGrid = n_terrain.createNode('grid', 'terrainGrid')
        hou.parm('/obj/terrain/terrainGrid/sizex').set(500)
        hou.parm('/obj/terrain/terrainGrid/sizey').set(500)
        hou.parm('/obj/terrain/terrainGrid/rows').set(150)
        hou.parm('/obj/terrain/terrainGrid/cols').set(150)
        n_terrainGrid.setPosition(hou.Vector2(0, 0))  
        
        # Create attribute from parameter node
        global n_attribFromMap
        n_attribFromMap = n_terrain.createNode('attribfrommap', 'attribfrommap')
        global filepaths
        hou.parm('/obj/terrain/attribfrommap/filename').set(filepaths[0])
        hou.parm('/obj/terrain/attribfrommap/uv_invertv').set(1)
        hou.parm('/obj/terrain/attribfrommap/srccolorspace').set("linear")
        n_attribFromMap.setPosition(hou.Vector2(2, 0)) 
        n_attribFromMap.setInput(0, n_terrainGrid)

        # Create Python node 
        n_python = n_terrain.createNode('python', 'python')
        pythonScript = loadVexString('/Users/natashadaas/houdiniCapstone/helperScripts/pythonScript.txt')
        hou.parm('/obj/terrain/python/python').set(pythonScript)
        n_python.setPosition(hou.Vector2(4, 0))
        n_python.setInput(0, n_attribFromMap)

        # Create attribute promote node
        n_attrib_promote = n_terrain.createNode("attribpromote", "attribpromote")
        hou.parm('/obj/terrain/attribpromote/inname').set("Cd")
        hou.parm('/obj/terrain/attribpromote/outclass').set(1)
        hou.parm('/obj/terrain/attribpromote/deletein').set(0)
        n_attrib_promote.setPosition(hou.Vector2(6, 0)) 
        n_attrib_promote.setInput(0, n_python)

        # Create attribute wrangle node
        n_attrib_wrangle = n_terrain.createNode('attribwrangle', 'attribwrangle')
        hou.parm('/obj/terrain/attribwrangle/class').set(1)
        terrainAttribWrangleVEXpression = loadVexString('/Users/natashadaas/houdiniCapstone/helperScripts/terrainAttribWrangleVEXpression.txt')
        hou.parm('/obj/terrain/attribwrangle/snippet').set(terrainAttribWrangleVEXpression)
        n_attrib_promote.setPosition(hou.Vector2(8, 0)) 
        n_attrib_wrangle.setInput(0, n_attrib_promote)

        # Create polyextrude node
        n_polyextrude_terrain = n_terrain.createNode("polyextrude", "polyextrude")
        hou.parm('/obj/terrain/polyextrude/splittype').set(0)
        hou.parm('/obj/terrain/polyextrude/dist').set(1.0)
        hou.parm('/obj/terrain/polyextrude/outputback').set(1)
        hou.parm('/obj/terrain/polyextrude/uselocalzscaleattrib').set(1)
        hou.parm('/obj/terrain/polyextrude/localzscaleattrib').set("zextrusion")
        n_polyextrude_terrain.setPosition(hou.Vector2(10, 0)) 
        n_polyextrude_terrain.setInput(0, n_attrib_wrangle)
        
        # Create heightfield node
        n_heightfield = n_terrain.createNode("heightfield", "heightfield")
        hou.parm('/obj/terrain/heightfield/sizex').set(500)
        hou.parm('/obj/terrain/heightfield/sizey').set(500)
        
        # Create heightfield project node
        n_heightfield_project = n_terrain.createNode("heightfield_project", "heightfield_project")
        n_heightfield_project.setInput(0, n_heightfield)
        n_heightfield_project.setInput(1, n_polyextrude_terrain)
        
        # Create heightfield blur node
        n_heightfield_blur = n_terrain.createNode("heightfield_blur", "heightfield_blur")
        hou.parm('/obj/terrain/heightfield_blur/radius').set(22)
        n_heightfield_blur.setInput(0, n_heightfield_project)
        
        # Create heightfield noise node
        n_heightfield_noise = n_terrain.createNode("heightfield_noise", "heightfield_noise")
        hou.parm('/obj/terrain/heightfield_noise/elementsize').set(275)
        n_heightfield_noise.setInput(0, n_heightfield_blur)
        
        hou.node('/obj/terrain/attribfrommap').setDisplayFlag(True)
        
        n_terrain.layoutChildren()
        
        # Call getAttribMapColors with self
        getAttribMapColors(self, n_attribFromMap)

def getAttribMapColors(self, node):
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
    global hexColorCodeGroups
    
    for scaled_color, count in color_groups.items():
        if count >= 20:
            hexColorCodeGroups.append(rgb_to_hex(scaled_color).strip())
            #print(f"Scaled Color: {scaled_color}, Count: {count}, Hex: {rgb_to_hex(scaled_color)}")
            
    addHexColorCodeGroupsToGUI(self)

class ColorDisplayFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, index=0, frameColor="#FFFFFF"):
        super(ColorDisplayFrame, self).__init__(parent)
        self.index = index
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setStyleSheet(f"background-color: {frameColor};")  # Default color
        self.setMinimumSize(50, 25)
        self.frameColor = frameColor

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
            oldColor = self.frameColor
            color = color_dialog.currentColor()  # Get the selected color
            if color.isValid():
                # Update the QFrame (color display box) background to the selected color
                self.setStyleSheet(f"background-color: {color.name()};")


                printHexColors()
                print(f"\n index: {self.index}")
                global hexColorCodeGroups
                hexColorCodeGroups[self.index] = color.name() 
                newColor = color.name()

                updatePythonScript(oldColor, newColor)
                printHexColors()

        color_dialog.deleteLater()  # Clean up the dialog after use
          
def selectMap():
    global initial_directory
    filepath, _ = QFileDialog.getOpenFileName(None, "Select Image", initial_directory, "Images (*.png *.jpg *.bmp)")
    if filepath:
        print(f"Selected file: {filepath}")
        global filepaths
        filepaths.append(filepath)

# Show the widget
def show_widget():
    widget = MyWidget()
    widget.show()
    
show_widget()
