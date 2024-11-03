import hou
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtWidgets import QFileDialog
from collections import defaultdict

global initial_directory
initial_directory = "/Users/natashadaas/houdiniCapstone/inputImages/"

global filepaths
filepaths = []

global n_attribFromMap

global terrainColorsInHex 
terrainColorsInHex = []

global color_tuples
color_tuples = []

global terrain_part_wrangle_nodes
terrain_part_wrangle_nodes = []

global terrain_part_color_nodes
terrain_part_color_nodes = []

def printParms(node):
    for p in node.parms():
        print(p)
        print(p.eval())

def loadVexString(filename):
    with open(filename, 'r') as file:
        vex_code_string = file.read()
    return vex_code_string

def printHexColors():
    for i in range(len(terrainColorsInHex)):
        print(f"{i}: {terrainColorsInHex[i]}")

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
    for i in range(len(terrainColorsInHex)):  # Adjust the range for the number of rows
        label = QtWidgets.QLabel(f"Color {i + 1}")
        color_display_frame = ColorDisplayFrame(self, index=i, frameColor=terrainColorsInHex[i])  # Custom QFrame

        color_grid_widget = self.ui.colorGridScrollArea.widget()  # Access colorGridWidget
        color_grid_layout = color_grid_widget.layout() 

        # Add to grid layout (label on the left, color display frame on the right)
        color_grid_layout.addWidget(label, i + 1, 0)
        color_grid_layout.addWidget(color_display_frame, i + 1, 1)

def updateAttribMapColors():
    print("update")

def generateTerrainColorSectionExtractionVEXExpression(hexColor):
    sectionRGBColors = hexToRGB(hexColor)
    rScaledDown = sectionRGBColors[0]/255
    gScaledDown = sectionRGBColors[1]/255
    bScaledDown = sectionRGBColors[2]/255
    targetValuesSetUp = f"float targetR = {rScaledDown};\nfloat targetG = {gScaledDown};\nfloat targetB = {bScaledDown};\n"
    differenceValuesSetUp = "float differenceR = @Cd.r - targetR;\nfloat differenceG = @Cd.g - targetG;\nfloat differenceB = @Cd.b - targetB;\n"
    conditionSetUp = "if (!(differenceR < 0.1 && differenceR > -0.1 && differenceG < 0.1 && differenceG > -0.1 && differenceB < 0.1 && differenceB > -0.1)) {"
    conditionEnd = "\n\tremovepoint(0,@ptnum);\n}"
    
    fileContent = targetValuesSetUp + differenceValuesSetUp + conditionSetUp + conditionEnd
    
    with open('/Users/natashadaas/houdiniCapstone/helperScripts/terrainColorSectionExtractionVexExpression.txt', "w") as file:
        file.write(fileContent)

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
        n_attribFromMap.setPosition(hou.Vector2(0, -2)) 
        n_attribFromMap.setInput(0, n_terrainGrid)

        # Call getAttribMapColors with self - display different colors found and populate terrainColorsInHex
        getAttribMapColors(self, n_attribFromMap)

        # Create attribute wrangle node for each color
        global terrainColorsInHex
        global terrain_part_wrangle_nodes
        for i in range(len(terrainColorsInHex)):
            attrib_wrangle_name = 'attribwrangle' + str(i)
            new_attrib_wrangle = n_terrain.createNode('attribwrangle', attrib_wrangle_name)
            sectionHexColor = terrainColorsInHex[i]
            generateTerrainColorSectionExtractionVEXExpression(sectionHexColor)
            vexExpression = loadVexString('/Users/natashadaas/houdiniCapstone/helperScripts/terrainColorSectionExtractionVexExpression.txt')
            hou.parm(f'/obj/terrain/{new_attrib_wrangle}/snippet').set(vexExpression)
            new_attrib_wrangle.setPosition(hou.Vector2(i*2, -4)) 
            new_attrib_wrangle.setInput(0, n_attribFromMap)
            terrain_part_wrangle_nodes.append(new_attrib_wrangle)

        # Create color node for each color and attach it to its attribute wrangle node
        for i in range(len(terrainColorsInHex)):
            color_name = 'color' + str(i)
            new_color_node = n_terrain.createNode("color", color_name)
            sectionRGBColors = hexToRGB(terrainColorsInHex[i])
            rScaledDown = round(sectionRGBColors[0]/255,2)
            gScaledDown = round(sectionRGBColors[1]/255,2)
            bScaledDown = round(sectionRGBColors[2]/255,2)
            new_color_node.parmTuple("color").set((rScaledDown, gScaledDown, bScaledDown))
            new_color_node.setPosition(hou.Vector2(i*2, -6)) 
            targetAttribNode = hou.node(f'/obj/terrain/attribwrangle{i}')
            new_color_node.setInput(0, targetAttribNode)
            terrain_part_color_nodes.append(new_color_node)

        # Create object merge node to merge back all colors together, ready for extrusion
        n_merge_colors = n_terrain.createNode('merge', "merge_colors")
        for i in range(len(terrainColorsInHex)):
            attribWrangleNode = hou.node(f'/obj/terrain/color{i}/')
            n_merge_colors.setInput(i, attribWrangleNode)
        n_merge_colors.setPosition(hou.Vector2(0,-6))

        # Create attribute promote node
        n_attrib_promote = n_terrain.createNode("attribpromote", "attribpromote")
        hou.parm('/obj/terrain/attribpromote/inname').set("Cd")
        hou.parm('/obj/terrain/attribpromote/outclass').set(1)
        hou.parm('/obj/terrain/attribpromote/deletein').set(0)
        n_attrib_promote.setPosition(hou.Vector2(6, 0)) 
        n_attrib_promote.setInput(0, n_merge_colors)

        # Create attribute wrangle node
        n_attrib_wrangle = n_terrain.createNode('attribwrangle', 'attribwrangleforextrusion')
        hou.parm('/obj/terrain/attribwrangleforextrusion/class').set(1)
        terrainAttribWrangleVEXpression = loadVexString('/Users/natashadaas/houdiniCapstone/helperScripts/terrainAttribWrangleVEXpression.txt')
        hou.parm('/obj/terrain/attribwrangleforextrusion/snippet').set(terrainAttribWrangleVEXpression)
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
        
        hou.node('/obj/terrain/heightfield_noise').setDisplayFlag(True)
        
        n_terrain.layoutChildren()
        

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
    global terrainColorsInHex
    
    for scaled_color, count in color_groups.items():
        if count >= 20:
            terrainColorsInHex.append(rgb_to_hex(scaled_color).strip())
            #print(f"Scaled Color: {scaled_color}, Count: {count}, Hex: {rgb_to_hex(scaled_color)}")
            
    addHexColorCodeGroupsToGUI(self)

# update the color node of the specific part to the new hex color
def changeColorOnMap(index, newHexColor):
    newRGBColors = hexToRGB(newHexColor)
    rScaledDown = round(newRGBColors[0]/255,2)
    gScaledDown = round(newRGBColors[1]/255,2)
    bScaledDown = round(newRGBColors[2]/255,2)
    targetColorNode = hou.node(f'/obj/terrain/color{index}/')
    targetColorNode.parmTuple("color").set((rScaledDown, gScaledDown, bScaledDown))
    targetColorNode

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
            color = color_dialog.currentColor()  # Get the selected color
            if color.isValid():
                # Update the QFrame (color display box) background to the selected color
                self.setStyleSheet(f"background-color: {color.name()};")

                printHexColors()
                print(f"\n index: {self.index}")
                global terrainColorsInHex
                terrainColorsInHex[self.index] = color.name() 
                changeColorOnMap(self.index, color.name())

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
