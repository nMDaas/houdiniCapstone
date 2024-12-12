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

global g_waterColorsInHex
g_waterColorsInHex = []

global idColorsHex
idColorsHex = []

global g_ColorDisplayFrames
g_ColorDisplayFrames = []

global g_BrightnessValues
g_BrightnessValues = []

global color_tuples
color_tuples = []

global terrain_part_wrangle_nodes
terrain_part_wrangle_nodes = []

global id_part_wrangle_nodes
id_part_wrangle_nodes = []

global terrain_part_color_nodes
terrain_part_color_nodes = []

# global array that determines whether an id receives noise or not
global g_IDNoiseBool
g_IDNoiseBool = []

# stores different terrain options
global g_TerrainOptions
g_TerrainOptions = []

# stores current dropdown values for each id
global g_DropdownValues
g_DropdownValues = []

g_TerrainOptions.append("Terrain Noise")
g_TerrainOptions.append("Flat Land")

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

def printGBrightnessValues():
    global g_BrightnessValues
    for i in range(len(g_BrightnessValues)):
        print(f"{i}: {g_BrightnessValues[i]}")

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

def rgb_to_brightness(rgb_tuple):
    r, g, b = rgb_tuple
    brightness = (r + g + b) / 3

    return brightness

def rgb_brightened_by_val(rgb_tuple, new_brightness):
    # Convert the RGB values from 0-1 range to 0-255 range
    r, g, b = rgb_tuple

    # Calculate the current brightness in the 0-255 range
    current_brightness = rgb_to_brightness((r, g, b))
    scale_factor = new_brightness / current_brightness if current_brightness != 0 else 1

    # Apply the scaling factor
    r_new = r * scale_factor
    g_new = g * scale_factor
    b_new = b * scale_factor

    return (r_new, g_new, b_new)

def addWaterGroupsToGUI(self):
    global g_waterColorsInHex
    print("len(idColorsHex): " + str(len(g_waterColorsInHex)))
    for i in range(len(g_waterColorsInHex)):  # Adjust the range for the number of rows
        label = QtWidgets.QLabel(f"{g_waterColorsInHex[i]}")
        color_display_frame = ColorDisplayFrame(self, index=i, frameColor=g_waterColorsInHex[i])  # Custom QFrame
    
        water_grid_widget = self.ui.waterGridScrollArea.widget()  # Access colorGridWidget
        water_grid_layout = water_grid_widget.layout() 

        # Create a text entry box (QLineEdit)
        text_entry = QtWidgets.QLineEdit()
        text_entry.setPlaceholderText("Enter Height on Y Axis")  # Optional placeholder text
        text_entry.textChanged.connect(lambda text, idx=i: self.handleHeightInputChange(text, idx))

        # Access the water grid widget and layout
        water_grid_widget = self.ui.waterGridScrollArea.widget()
        water_grid_layout = water_grid_widget.layout()

        # Add to grid layout (label on the left, color display frame on the right)
        water_grid_layout.addWidget(label, i + 1, 0)
        water_grid_layout.addWidget(color_display_frame, i + 1, 1)
        water_grid_layout.addWidget(text_entry, i + 1, 2)

def addIDGroupsToGUI(self):
    global idColorsHex
    global g_DropdownValues
    #print("len(idColorsHex): " + str(len(idColorsHex)))
    for i in range(len(idColorsHex)):  # Adjust the range for the number of rows
        label = QtWidgets.QLabel(f"{idColorsHex[i]}")
        color_display_frame = ColorDisplayFrame(self, index=i, frameColor=idColorsHex[i])  # Custom QFrame
        #global g_ColorDisplayFrames
        #g_ColorDisplayFrames.append(color_display_frame)

        id_grid_widget = self.ui.idGridScrollArea.widget()  # Access colorGridWidget
        id_grid_layout = id_grid_widget.layout() 

        # Create a dropdown
        dropdown_box = QtWidgets.QComboBox()
        dropdown_box.addItem("Select Texture")
        items = ["Terrain Noise", "Flat Land"]
        dropdown_box.addItems(items)

        # Connect signal for selection detection
        dropdown_box.currentIndexChanged.connect(lambda index, row=i: self.on_dropdown_changed(index, row))

        # Add to grid layout (label on the left, color display frame on the right)
        id_grid_layout.addWidget(label, i + 1, 0)
        id_grid_layout.addWidget(color_display_frame, i + 1, 1)
        id_grid_layout.addWidget(dropdown_box, i + 1, 2)

def addHexColorCodeGroupsToGUI(self):
    # Add labels and color display frames to the grid layout
    for i in range(len(terrainColorsInHex)):  # Adjust the range for the number of rows
        label = QtWidgets.QLabel(f"{terrainColorsInHex[i]}")
        color_display_frame = ColorDisplayFrame(self, index=i, frameColor=terrainColorsInHex[i])  # Custom QFrame
        global g_ColorDisplayFrames
        g_ColorDisplayFrames.append(color_display_frame)

        color_grid_widget = self.ui.colorGridScrollArea.widget()  # Access colorGridWidget
        color_grid_layout = color_grid_widget.layout() 

        # Create an input box for editing the hex color
        input_box = QtWidgets.QLineEdit()
        global g_BrightnessValues
        initialBrightness = str(rgb_to_brightness(hexToRGB(terrainColorsInHex[i])))
        g_BrightnessValues.append(initialBrightness)
        input_box.setPlaceholderText("Enter Height")
        input_box.setText(initialBrightness)  # Pre-fill with the current hex code
        input_box.setMaximumWidth(100)  # Adjust the width of the input box if needed
        # Connect the input box text change signal to the method that handles it
        input_box.textChanged.connect(lambda text, idx=i: self.handleInputChange(text, idx))


        # Add to grid layout (label on the left, color display frame on the right)
        color_grid_layout.addWidget(label, i + 1, 0)
        color_grid_layout.addWidget(color_display_frame, i + 1, 1)
        color_grid_layout.addWidget(input_box, i + 1, 2)

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

def init_g_IDNoiseBool():
    global g_IDNoiseBool
    for i in range(len(idColorsHex)):
        g_IDNoiseBool.append(0)

# Create Terrain Texture Node
def createTerrainTexture(self):
        
    # Create terrain Geometry node
    OBJ = hou.node('/obj/')
    n_terrain_texture = OBJ.createNode('geo', 'terrain_texture')

    # Create heightfield node
    n_heightfield = n_terrain_texture.createNode("heightfield", "heightfield")

    hou.parm('/obj/terrain_texture/heightfield/sizex').set(500)
    hou.parm('/obj/terrain_texture/heightfield/sizey').set(500)

    # Create an object merge node that pulls from terrain_height's OUT node
    n_terrain_height_merge = n_terrain_texture.createNode("object_merge", "terrain_height_merge")
    hou.parm(f'/obj/terrain_texture/terrain_height_merge//objpath1').set('../../terrain_height/OUT_TERRAIN_HEIGHT')

    # Create heightfield project node
    n_heightfield_project = n_terrain_texture.createNode("heightfield_project", "heightfield_project")
    n_heightfield_project.setInput(0, n_heightfield)
    n_heightfield_project.setInput(1, n_terrain_height_merge)
    
    n_heightfield_blur = n_terrain_texture.createNode("heightfield_blur", "heightfield_blur")
    hou.parm('/obj/terrain_texture/heightfield_blur/radius').set(22)
    n_heightfield_blur.setInput(0, n_heightfield_project)

    lastNode = n_heightfield_blur
    
    global idColorsHex
    init_g_IDNoiseBool() #initially this global sets every texture to not have noise 

    global g_IDNoiseBool

    for i in range(len(idColorsHex)):

        if (g_IDNoiseBool[i] == 1):
            # create a object merge node that gets OUT_id{i}
            merge_node_name = 'merge_id' + str(i)
            new_merge_node = n_terrain_texture.createNode("object_merge", merge_node_name)
            new_merge_node.setPosition(hou.Vector2(8, -14-(i*5))) 
            target_id_object = f'/obj/id/OUT_id{i}'
            hou.parm(f'/obj/terrain_texture/{merge_node_name}/objpath1').set(target_id_object)

            # create a heightfield mask by object node that takes in n_heightfield_project and the object merge node as input
            mask_node_name = 'mask_id' + str(i)
            new_mask_node = n_terrain_texture.createNode("heightfield_maskbyobject", mask_node_name)
            new_mask_node.setInput(0, lastNode) 
            new_mask_node.setInput(1, new_merge_node) 
            new_mask_node.setPosition(hou.Vector2(6, -14-(i*5))) 
            hou.parm(f'/obj/terrain_texture/{mask_node_name}/blurradius').set(23)

            # Create noise node that takes in the blur and the mask node as input
            noise_node_name = 'noise' + str(i) 
            new_noise_node = n_terrain_texture.createNode("heightfield_noise", noise_node_name)
            hou.parm(f'/obj/terrain_texture/{noise_node_name}/elementsize').set(275)
            new_noise_node.setInput(0, lastNode)
            new_noise_node.setInput(1, new_mask_node)
            new_noise_node.setPosition(hou.Vector2(4, -18-(i*5))) 

            lastNode = new_noise_node

        # Create a null node to mark the end of editing this ID
        null_name = 'OUT_terrain_id' + str(i)
        new_null_node = n_terrain_texture.createNode("null", null_name)
        new_null_node.setInput(0, lastNode)
        new_null_node.setPosition(hou.Vector2(4, -20-(i*5))) 
        lastNode = new_null_node

    n_null = n_terrain_texture.createNode("null", "OUT_TERRAIN_TEXTURE")
    n_null.setInput(0, lastNode)
    n_null.setPosition(hou.Vector2(12,0)) 

    # add convert node
    n_convert = n_terrain_texture.createNode("convert", "convert_to_polygons")
    n_convert.setInput(0, n_null)

    # Add polyreduce node
    n_polyreduce = n_terrain_texture.createNode("polyreduce", "polyreduce")
    n_polyreduce.setInput(0, n_convert)
    n_polyreduce.parm("percentage").set(100)  # Set reduction percentage (adjust as needed)

    n_terrain_texture.layoutChildren()
    n_polyreduce.setDisplayFlag(True) 
    hou.node('obj/id/').setDisplayFlag(False)
    hou.node('obj/terrain_height/').setDisplayFlag(False)

    #addIDGroupsToGUI(self)

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
        self.ui.select_button.clicked.connect(self.selectHeightMap)
        self.ui.reload_button.clicked.connect(self.reload)
        self.ui.reload_id_button.clicked.connect(self.reload_id)
        self.ui.original_image_button.clicked.connect(self.showOriginalImage)
        self.ui.modified_image_button.clicked.connect(self.showModifiedImage)
        self.ui.extrusion_button.clicked.connect(self.showExtrusion)
        self.ui.select_id_button.clicked.connect(self.selectTextureIDMap)
        self.ui.select_water_button.clicked.connect(self.selectWaterMap)
        self.ui.reload_water_button.clicked.connect(self.reload_water)
        self.ui.texture_map_button.clicked.connect(self.showTextureIDMap)
        self.ui.texture_terrain_button.clicked.connect(self.showTexturedTerrain)
        self.ui.water_map_button.clicked.connect(self.showWaterMap)
        self.ui.water_geo_button.clicked.connect(self.showWaterGeo)

        # Connect the QLineEdit to a function for LOD changes
        self.ui.LODEntryBox.textChanged.connect(self.on_LOD_level_change)

    def on_LOD_level_change(self):
        text = self.ui.LODEntryBox.text()
        n_polyreduce = hou.node('obj/terrain_texture/polyreduce')
        n_polyreduce.parm("percentage").set(int(text))
        print(f"Text changed: {text}")

    def handleHeightInputChange(self, new_text, idx):
        hou.parm(f'/obj/water/transform{idx}/ty').set(float(new_text))

    def handleInputChange(self, new_text, idx):
        # update the brightness in the global g_BrightnessValues map
        global g_BrightnessValues
        g_BrightnessValues[idx] = float(new_text)
        
        # calculate the brightened color
        global terrainColorsInHex
        old_hex_color = terrainColorsInHex[idx]
        old_rgb_color = hexToRGB(old_hex_color)
        new_rgb_tuple = rgb_brightened_by_val(old_rgb_color, int(new_text))
        new_hex_color = rgb_to_hex(new_rgb_tuple)

        # update the color of the correct display frame
        global g_ColorDisplayFrames
        g_ColorDisplayFrames[idx].change_color(new_hex_color)

        # update global variable terrainColorsInHex and change color on the map in Houdini
        terrainColorsInHex[idx] = new_hex_color
        changeColorOnMap(idx, new_hex_color)

    def on_dropdown_changed(self, index, row):
        global g_TerrainOptions

        # Access the selected dropdown box text
        dropdown_box = self.ui.idGridScrollArea.widget().layout().itemAtPosition(row + 1, 2).widget()
        #print(g_TerrainOptions[index - 1])  # Check the value you're passing
        #print([dropdown_box.itemText(i) for i in range(dropdown_box.count())])  # Check all dropdown items
        dropdown_box.setCurrentIndex(index)
        selected_text = g_TerrainOptions[index - 1]

        global g_IDNoiseBool
        
        # Handle the selected value
        #print(f"Row {row}: Selected index {index}, Text: {selected_text}")
        if selected_text == "Select Texture":
            print("No valid option selected.")
        elif selected_text == "Terrain Noise":
            g_IDNoiseBool[row] = 1 #this id should be set to true for the noise map
            n_terrain_texture = hou.node('/obj/terrain_texture/')
            n_terrain_texture.destroy()
            createTerrainTexture(self)
        elif selected_text == "Flat Land":
            g_IDNoiseBool[row] = 0 #this id should be set to false for the noise map
            n_terrain_texture = hou.node('/obj/terrain_texture/')
            n_terrain_texture.destroy()
            createTerrainTexture(self)
        else:
            print(f"Row {row}: You selected {selected_text}.")

    def apply(self):
        # Create terrain Height node
        OBJ = hou.node('/obj/')
        n_terrain = OBJ.createNode('geo', 'terrain_height')
        
        # Create grid node in terrain node
        n_terrainGrid = n_terrain.createNode('grid', 'terrainGrid')
        hou.parm('/obj/terrain_height/terrainGrid/sizex').set(500)
        hou.parm('/obj/terrain_height/terrainGrid/sizey').set(500)
        hou.parm('/obj/terrain_height/terrainGrid/rows').set(150)
        hou.parm('/obj/terrain_height/terrainGrid/cols').set(150)
        n_terrainGrid.setPosition(hou.Vector2(0, 0))  
        
        # Create attribute from parameter node
        global n_attribFromMap
        n_attribFromMap = n_terrain.createNode('attribfrommap', 'attribfrommap')
        global filepaths
        hou.parm('/obj/terrain_height/attribfrommap/filename').set(filepaths[0])
        hou.parm('/obj/terrain_height/attribfrommap/uv_invertv').set(1)
        hou.parm('/obj/terrain_height/attribfrommap/srccolorspace').set("linear")
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
            hou.parm(f'/obj/terrain_height/{new_attrib_wrangle}/snippet').set(vexExpression)
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
            targetAttribNode = hou.node(f'/obj/terrain_height/attribwrangle{i}')
            new_color_node.setInput(0, targetAttribNode)
            terrain_part_color_nodes.append(new_color_node)

        # Create object merge node to merge back all colors together, ready for extrusion
        n_merge_colors = n_terrain.createNode('merge', "merge_colors")
        for i in range(len(terrainColorsInHex)):
            attribWrangleNode = hou.node(f'/obj/terrain_height/color{i}/')
            n_merge_colors.setInput(i, attribWrangleNode)
        n_merge_colors.setPosition(hou.Vector2(0,-6))

        # Create attribute promote node
        n_attrib_promote = n_terrain.createNode("attribpromote", "attribpromote")
        hou.parm('/obj/terrain_height/attribpromote/inname').set("Cd")
        hou.parm('/obj/terrain_height/attribpromote/outclass').set(1)
        hou.parm('/obj/terrain_height/attribpromote/deletein').set(0)
        n_attrib_promote.setPosition(hou.Vector2(6, 0)) 
        n_attrib_promote.setInput(0, n_merge_colors)

        # Create attribute wrangle node
        n_attrib_wrangle = n_terrain.createNode('attribwrangle', 'attribwrangleforextrusion')
        hou.parm('/obj/terrain_height/attribwrangleforextrusion/class').set(1)
        terrainAttribWrangleVEXpression = loadVexString('/Users/natashadaas/houdiniCapstone/helperScripts/terrainAttribWrangleVEXpression.txt')
        hou.parm('/obj/terrain_height/attribwrangleforextrusion/snippet').set(terrainAttribWrangleVEXpression)
        n_attrib_promote.setPosition(hou.Vector2(8, 0)) 
        n_attrib_wrangle.setInput(0, n_attrib_promote)

        # Create polyextrude node
        n_polyextrude_terrain = n_terrain.createNode("polyextrude", "polyextrude")
        hou.parm('/obj/terrain_height/polyextrude/splittype').set(0)
        hou.parm('/obj/terrain_height/polyextrude/dist').set(1.0)
        hou.parm('/obj/terrain_height/polyextrude/outputback').set(1)
        hou.parm('/obj/terrain_height/polyextrude/uselocalzscaleattrib').set(1)
        hou.parm('/obj/terrain_height/polyextrude/localzscaleattrib').set("zextrusion")
        n_polyextrude_terrain.setPosition(hou.Vector2(10, 0)) 
        n_polyextrude_terrain.setInput(0, n_attrib_wrangle)

        # Create a null node for OUT_TERRAIN_HEIGHT
        n_null = n_terrain.createNode("null", "OUT_TERRAIN_HEIGHT")
        n_null.setInput(0, n_polyextrude_terrain)
        n_null.setPosition(hou.Vector2(12,0)) 

        n_terrain.layoutChildren()
        hou.node('/obj/terrain_height/polyextrude').setDisplayFlag(True)
        
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
        
    def selectHeightMap(self):
        print("HIIII")
        global initial_directory
        filepath, _ = QFileDialog.getOpenFileName(None, "Select Image", initial_directory, "Images (*.png *.jpg *.bmp)")
        if filepath:
            print(f"Selected file: {filepath}")
            global filepaths
            filepaths.append(filepath)
            self.apply()

    def selectTextureIDMap(self):
        global initial_directory
        filepath, _ = QFileDialog.getOpenFileName(None, "Select Image", initial_directory, "Images (*.png *.jpg *.bmp)")
        if filepath:
            print(f"Selected file: {filepath}")
            global filepaths
            filepaths.append(filepath)
            self.applyIdMap()

    def selectWaterMap(self):
        global initial_directory
        filepath, _ = QFileDialog.getOpenFileName(None, "Select Image", initial_directory, "Images (*.png *.jpg *.bmp)")
        if filepath:
            print(f"Selected file: {filepath}")
            global filepaths
            filepaths.append(filepath)
            self.applyWaterMap()

    def reload(self):
        hou.parm('/obj/terrain_height/attribfrommap/reload').pressButton()

        #delete terrain object
        n_terrain = hou.node('/obj/terrain_height/')
        n_terrain.destroy()
        global terrainColorsInHex
        terrainColorsInHex.clear()

        self.apply()

    def reload_id(self):
        hou.parm('/obj/id/id_attribfrommap/reload').pressButton()

        #delete id object
        n_id = hou.node('/obj/id/')
        n_id.destroy()

        #delete terrain_texture object
        n_terrain_texture = hou.node('/obj/terrain_texture/')
        n_terrain_texture.destroy()

        global idColorsHex
        idColorsHex.clear()

        global id_part_wrangle_nodes
        id_part_wrangle_nodes.clear()

        global g_DropdownValues
        g_DropdownValues.clear()

        global g_IDNoiseBool
        g_IDNoiseBool.clear

        id_grid_widget = self.ui.idGridScrollArea.widget()  # Access colorGridWidget
        id_grid_layout = id_grid_widget.layout() 

        # Remove all widgets in the layout
        for i in reversed(range(id_grid_layout.count())):
            widget = id_grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater() 

        self.applyIdMap()

    def reload_water(self):
        hou.parm('/obj/water/waterattribfrommap/reload').pressButton()

        #delete water object
        n_water = hou.node('/obj/water/')
        n_water.destroy()

        global g_waterColorsInHex
        g_waterColorsInHex.clear()

        water_grid_widget = self.ui.waterGridScrollArea.widget()  # Access colorGridWidget
        water_grid_layout = water_grid_widget.layout() 

        # Remove all widgets in the layout
        for i in reversed(range(water_grid_layout.count())):
            widget = water_grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater() 

        self.applyWaterMap()

    def showOriginalImage(self):
        hou.node('/obj/terrain_height/attribfrommap').setDisplayFlag(True)

    def showModifiedImage(self):
        hou.node('/obj/terrain_height/merge_colors').setDisplayFlag(True)

    def showExtrusion(self):
        hou.node('/obj/terrain_height/polyextrude').setDisplayFlag(True)
   
    def showTextureIDMap(self):
        hou.node('/obj/terrain_texture').setDisplayFlag(False)
        hou.node('/obj/id').setDisplayFlag(True)

    def showTexturedTerrain(self):
        hou.node('/obj/terrain_texture').setDisplayFlag(True)
        hou.node('/obj/id').setDisplayFlag(False)
        #hou.node('/obj/id/').setDisplayFlag(False)
        #hou.node('/obj/terrain_texture/polyreduce').setDisplayFlag(True)

    def showWaterMap(self):
        hou.node('/obj/terrain_texture').setDisplayFlag(False)
        hou.node('/obj/water/waterattribfrommap').setDisplayFlag(True)

    def showWaterGeo(self):
        hou.node('/obj/terrain_texture').setDisplayFlag(True)
        hou.node('/obj/water/merge_water').setDisplayFlag(True)


    def applyWaterMap(self):
        # Create water Geometry node
        OBJ = hou.node('/obj/')
        n_water = OBJ.createNode('geo', 'water')

        # Create grid node in water node
        n_waterGrid = n_water.createNode('grid', 'waterGrid')
        hou.parm('/obj/water/waterGrid/sizex').set(500)
        hou.parm('/obj/water/waterGrid/sizey').set(500)
        hou.parm('/obj/water/waterGrid/rows').set(150)
        hou.parm('/obj/water/waterGrid/cols').set(150)
        n_waterGrid.setPosition(hou.Vector2(0, 0))  
        
        # Create attribute from parameter node
        global n_attribFromMap
        n_attribFromMap = n_water.createNode('attribfrommap', 'waterattribfrommap')
        hou.parm('/obj/water/waterattribfrommap/filename').set(filepaths[2])
        hou.parm('/obj/water/waterattribfrommap/uv_invertv').set(1)
        hou.parm('/obj/water/waterattribfrommap/srccolorspace').set("linear")
        n_attribFromMap.setPosition(hou.Vector2(0, -2)) 
        n_attribFromMap.setInput(0, n_waterGrid)

        getAttribMapWaterColors(self, n_attribFromMap)

        # Create attribute wrangle node for each color
        global g_waterColorsInHex
        for i in range(len(g_waterColorsInHex)):
            attrib_wrangle_name = 'attribwrangle' + str(i)
            new_attrib_wrangle = n_water.createNode('attribwrangle', attrib_wrangle_name)
            sectionHexColor = g_waterColorsInHex[i]
            generateTerrainColorSectionExtractionVEXExpression(sectionHexColor)
            vexExpression = loadVexString('/Users/natashadaas/houdiniCapstone/helperScripts/terrainColorSectionExtractionVexExpression.txt')
            hou.parm(f'/obj/water/{new_attrib_wrangle}/snippet').set(vexExpression)
            new_attrib_wrangle.setPosition(hou.Vector2(i,-4)) 
            new_attrib_wrangle.setInput(0, n_attribFromMap)

        # Create color node for each water group to "neutralize" and remove color
        for i in range(len(g_waterColorsInHex)):
            color_name = 'color' + str(i)
            new_color_node = n_water.createNode("color", color_name)
            targetAttribNode = hou.node(f'/obj/water/attribwrangle{i}')
            new_color_node.setInput(0, targetAttribNode)

        # Create transform node for each water group
        for i in range(len(g_waterColorsInHex)):
            transform_name = 'transform' + str(i)
            new_transform_node = n_water.createNode("xform", transform_name)
            targetColorNode = hou.node(f'/obj/water/color{i}')
            new_transform_node.setInput(0, targetColorNode)

        # Create object merge node to merge all water bodies together
        n_merge_water = n_water.createNode('merge', "merge_water")
        for i in range(len(g_waterColorsInHex)):
            transformNode = hou.node(f'/obj/water/transform{i}/')
            n_merge_water.setInput(i, transformNode)
        n_merge_water.setPosition(hou.Vector2(0,-6))

        n_water.layoutChildren()

        hou.node('/obj/water/merge_water').setDisplayFlag(True)

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

        # dropdown values for each id should be initially not set
        global g_DropdownValues
        for i in range(len(idColorsHex)):
            g_DropdownValues.append("Select Texture")

        # Now that that's done, create masks in the terrain_texture node and create the heightfield based on ids
        createTerrainTexture(self)

        # add id colors to UI based on texture id map
        addIDGroupsToGUI(self)

        hou.node('/obj/id/id_attribfrommap').setDisplayFlag(True)

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

def getAttribMapWaterColors(self, node):
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

    global g_waterColorsInHex
    
    for scaled_color, count in color_groups.items():
        #print(f"Scaled Color: {scaled_color}, Count: {count}, Hex: {rgb_to_hex(scaled_color)}")
        notWater = (sum(scaled_color) / 3) < 30
        if count >= 20 and not notWater:
            g_waterColorsInHex.append(rgb_to_hex(scaled_color).strip())
            print(f"Scaled Color: {scaled_color}, Count: {count}, Hex: {rgb_to_hex(scaled_color)}")
            
    addWaterGroupsToGUI(self)

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
    targetColorNode = hou.node(f'/obj/terrain_height/color{index}/')
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

    def change_color(self, new_color):
        self.setStyleSheet(f"background-color: {new_color};")  # Make sure to use quotes around the color

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

# Show the widget
def show_widget():
    widget = MyWidget()
    widget.show()
    
show_widget()
