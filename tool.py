import hou
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtWidgets import QFileDialog
from collections import defaultdict
from PIL import Image

global initial_directory
initial_directory = "/Users/natashadaas/houdiniCapstone/inputImages/"

global filepaths
filepaths = []

global n_attribFromMap

global terrainColorsInHex 
terrainColorsInHex = []

global idColorsHex
idColorsHex = []

global color_tuples
color_tuples = []

global terrain_part_wrangle_nodes
terrain_part_wrangle_nodes = []

global id_part_wrangle_nodes
id_part_wrangle_nodes = []

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
    #print("hex_color: ", hex_color)
    hex_color = hex_color.lstrip('#')  # Remove '#' if present
    # Check that the length of the hex color is valid
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    else:
        raise ValueError("Invalid hex color format: must be a 6-digit hex string.")

def addHexColorCodeGroupsToGUI(self):
    # Add labels and color display frames to the grid layout
    for i in range(len(terrainColorsInHex)):  # Adjust the range for the number of rows
        label = QtWidgets.QLabel(f"{terrainColorsInHex[i]}")
        color_display_frame = ColorDisplayFrame(self, index=i, frameColor=terrainColorsInHex[i])  # Custom QFrame

        color_grid_widget = self.ui.colorGridScrollArea.widget()  # Access colorGridWidget
        color_grid_layout = color_grid_widget.layout() 

        # Add to grid layout (label on the left, color display frame on the right)
        color_grid_layout.addWidget(label, i + 1, 0)
        color_grid_layout.addWidget(color_display_frame, i + 1, 1)

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

def createHeightfieldFromMaps():

        n_terrain = hou.node('obj/terrain/')
        n_heightfield_project = hou.node('obj/terrain/heightfield_project')

        n_heightfield_blur = n_terrain.createNode("heightfield_blur", "heightfield_blur")
        hou.parm('/obj/terrain/heightfield_blur/radius').set(22)
        n_heightfield_blur.setInput(0, n_heightfield_project)

        lastNode = n_heightfield_blur
        
        global idColorsHex
        for i in range(len(idColorsHex)):
            # create a object merge node that gets OUT_id{i}
            merge_node_name = 'merge_id' + str(i)
            new_merge_node = n_terrain.createNode("object_merge", merge_node_name)
            new_merge_node.setPosition(hou.Vector2(8, -14-(i*5))) 
            target_id_object = f'/obj/id/OUT_id{i}'
            hou.parm(f'/obj/terrain/{merge_node_name}/objpath1').set(target_id_object)

            # create a heightfield mask by object node that takes in n_heightfield_project and the object merge node as input
            mask_node_name = 'mask_id' + str(i)
            new_mask_node = n_terrain.createNode("heightfield_maskbyobject", mask_node_name)
            new_mask_node.setInput(0, lastNode) 
            new_mask_node.setInput(1, new_merge_node) 
            new_mask_node.setPosition(hou.Vector2(6, -14-(i*5))) 
            hou.parm(f'/obj/terrain/{mask_node_name}/blurradius').set(23)

            # Create noise node that takes in the blur and the mask node as input
            noise_node_name = 'noise' + str(i) 
            new_noise_node = n_terrain.createNode("heightfield_noise", noise_node_name)
            hou.parm(f'/obj/terrain/{noise_node_name}/elementsize').set(275)
            new_noise_node.setInput(0, lastNode)
            new_noise_node.setInput(1, new_mask_node)
            new_noise_node.setPosition(hou.Vector2(4, -18-(i*5))) 

            # Create a null node to mark the end of editing this ID
            null_name = 'OUT_terrain_id' + str(i)
            new_null_node = n_terrain.createNode("null", null_name)
            new_null_node.setInput(0, new_noise_node)
            new_null_node.setPosition(hou.Vector2(4, -20-(i*5))) 
            lastNode = new_null_node

        lastNode.setDisplayFlag(True)
        hou.node('obj/id/').setDisplayFlag(False)

def testPrintImageHeightWidth():
    with Image.open('/Users/natashadaas/houdiniCapstone/media.jpg') as img:
        width, height = img.size

    print(f"Width: {width}, Height: {height}")

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        ui_file = '/Users/natashadaas/houdiniCapstone/gui.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        
        # Connect buttons to functions
        self.ui.select_button.clicked.connect(selectMap)
        self.ui.apply_button.clicked.connect(self.apply)
        self.ui.reload_button.clicked.connect(self.reload)
        self.ui.original_image_button.clicked.connect(self.showOriginalImage)
        self.ui.modified_image_button.clicked.connect(self.showModifiedImage)
        self.ui.extrusion_button.clicked.connect(self.showExtrusion)
        self.ui.select_id_button.clicked.connect(selectMap)
        self.ui.apply_id_button.clicked.connect(self.applyIdMap)

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
            #new_attrib_wrangle.setPosition(hou.Vector2(0,-4)) 
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

        n_terrain.layoutChildren()
        hou.node('/obj/terrain/polyextrude').setDisplayFlag(True)
        
        """

        # Create heightfield node
        n_heightfield = n_terrain.createNode("heightfield", "heightfield")
        hou.parm('/obj/terrain/heightfield/sizex').set(500)
        hou.parm('/obj/terrain/heightfield/sizey').set(500)
        
        # Create heightfield project node
        n_heightfield_project = n_terrain.createNode("heightfield_project", "heightfield_project")
        n_heightfield_project.setInput(0, n_heightfield)
        n_heightfield_project.setInput(1, n_polyextrude_terrain)

        hou.node('/obj/terrain/attribfrommap').setDisplayFlag(True)
        """
        
    def reload(self):
        hou.parm('/obj/terrain/attribfrommap/reload').pressButton()

        #delete terrain object
        n_terrain = hou.node('/obj/terrain/')
        n_terrain.destroy()
        global terrainColorsInHex
        terrainColorsInHex.clear()

        self.apply()

    def showOriginalImage(self):
        hou.node('/obj/terrain/attribfrommap').setDisplayFlag(True)

    def showModifiedImage(self):
        hou.node('/obj/terrain/merge_colors').setDisplayFlag(True)

    def showExtrusion(self):
        hou.node('/obj/terrain/polyextrude').setDisplayFlag(True)

    def applyIdMap(self):
        OBJ = hou.node('/obj/')
        n_id = OBJ.createNode('geo', 'id')
        n_id.setPosition(hou.Vector2(2, 0))  

        n_idGrid = n_id.createNode('grid', 'idGrid')
        hou.parm('/obj/id/idGrid/sizex').set(500)
        hou.parm('/obj/id/idGrid/sizey').set(500)
        hou.parm('/obj/id/idGrid/rows').set(150)
        hou.parm('/obj/id/idGrid/cols').set(150)
        n_idGrid.setPosition(hou.Vector2(0, 0))  
        
        # Create attribute from parameter node
        n_idAttribFromMap = n_id.createNode('attribfrommap', 'id_attribfrommap')
        global filepaths
        hou.parm('/obj/id/id_attribfrommap/filename').set(filepaths[1])
        hou.parm('/obj/id/id_attribfrommap/uv_invertv').set(1)
        hou.parm('/obj/id/id_attribfrommap/srccolorspace').set("linear")
        n_idAttribFromMap.setPosition(hou.Vector2(0, -2))  
        n_idAttribFromMap.setInput(0, n_idGrid)

        getIDAttribMapColors(self, n_idAttribFromMap)

        # Create attribute wrangle node for each color
        global idColorsHex
        global id_part_wrangle_nodes
        for i in range(len(idColorsHex)):
            attrib_wrangle_name = 'attribwrangle' + str(i)
            new_attrib_wrangle = n_id.createNode('attribwrangle', attrib_wrangle_name)
            sectionHexColor = idColorsHex[i]
            generateTerrainColorSectionExtractionVEXExpression(sectionHexColor)
            vexExpression = loadVexString('/Users/natashadaas/houdiniCapstone/helperScripts/terrainColorSectionExtractionVexExpression.txt')
            hou.parm(f'/obj/id/{new_attrib_wrangle}/snippet').set(vexExpression)
            new_attrib_wrangle.setPosition(hou.Vector2(i,-4)) 
            new_attrib_wrangle.setInput(0, n_idAttribFromMap)
            id_part_wrangle_nodes.append(new_attrib_wrangle)

        # Create color node for each color and attach it to its attribute wrangle node
        for i in range(len(idColorsHex)):
            color_name = 'color' + str(i)
            new_color_node = n_id.createNode("color", color_name)
            sectionRGBColors = hexToRGB(idColorsHex[i])
            rScaledDown = round(sectionRGBColors[0]/255,2)
            gScaledDown = round(sectionRGBColors[1]/255,2)
            bScaledDown = round(sectionRGBColors[2]/255,2)
            new_color_node.parmTuple("color").set((rScaledDown, gScaledDown, bScaledDown))
            new_color_node.setPosition(hou.Vector2(i*2, -6)) 
            targetAttribNode = hou.node(f'/obj/id/attribwrangle{i}')
            new_color_node.setInput(0, targetAttribNode)
            terrain_part_color_nodes.append(new_color_node)

        # Create a polyextrude node for each color and attach it to its color node
        for i in range(len(idColorsHex)):
            polyextrude_name = 'polyextrude' + str(i)
            new_polyextrude_node = n_id.createNode("polyextrude", polyextrude_name)
            hou.parm(f'/obj/id/{polyextrude_name}/splittype').set(0)
            hou.parm(f'/obj/id/{polyextrude_name}/dist').set(100.0)
            hou.parm(f'/obj/id/{polyextrude_name}/outputback').set(1)
            new_polyextrude_node.setPosition(hou.Vector2(i, -8)) 
            targetColorNode = hou.node(f'/obj/id/color{i}')
            new_polyextrude_node.setInput(0, targetColorNode)

        # Create a null node for each polyextrude and attach it to its polyextrude node
        for i in range(len(idColorsHex)):
            null_name = 'OUT_id' + str(i)
            new_null_node = n_id.createNode("null", null_name)
            new_null_node.setPosition(hou.Vector2(i, -10)) 
            targetPolyExtrudeNode = hou.node(f'/obj/id/polyextrude{i}')
            new_null_node.setPosition(hou.Vector2(i,-10)) 
            new_null_node.setInput(0, targetPolyExtrudeNode)

        # Now that that's done, create masks in the n_terrain node and create the heightfield based on ids
        createHeightfieldFromMaps()

def getIDAttribMapColors(self, node):
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

    global idColorsHex
    
    for scaled_color, count in color_groups.items():
        if count >= 20:
            idColorsHex.append(rgb_to_hex(scaled_color).strip())
            #print(f"Scaled Color: {scaled_color}, Count: {count}, Hex: {rgb_to_hex(scaled_color)}")

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
                #addHexColorCodeGroupsToGUI()

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
