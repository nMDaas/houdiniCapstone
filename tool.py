import hou
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtWidgets import QFileDialog, QColorDialog, QFrame


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        ui_file = '/Users/natashadaas/houdiniCapstone/gui.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        
        # Ensure the widget is set as a child of Houdini's main window
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        # Connect buttons to functions
        self.ui.select_button.clicked.connect(self.selectMap)
        self.ui.apply_button.clicked.connect(self.apply)
        self.ui.color_picker_button.clicked.connect(self.open_color_picker)

    def selectMap(self):
        initial_directory = "/Users/natashadaas/houdiniCapstone"
        dialog = QFileDialog(self)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setDirectory(initial_directory)
        dialog.setWindowTitle("Select Folder")

        if dialog.exec_() == QFileDialog.Accepted:
            self.filepaths = dialog.selectedFiles()
            print("filename: " + self.filepaths[0])
        else:
            print("No folder selected")

    def open_color_picker(self):
        # Open color picker dialog and get the selected color
        color_dialog = QColorDialog(self)  # Ensure it's parented
        color_dialog.setWindowTitle("Select Color")

        # Show the dialog as a non-modal dialog
        color_dialog.show()

        # Handle the accepted signal
        color_dialog.finished.connect(lambda result: self.handle_color_selection(result, color_dialog))

    def handle_color_selection(self, result, color_dialog):
        if result == 1:  # 1 means OK was clicked
            color = color_dialog.currentColor()  # Get the selected color
            if color.isValid():
                # Update the QFrame (color display box) background to the selected color
                self.ui.color_display_frame.setStyleSheet(f"background-color: {color.name()};")
        color_dialog.deleteLater()  # Clean up the dialog after use

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

        # Create attribute from parameter node
        n_attribFromMap = n_terrain.createNode('attribfrommap', 'attribfrommap')
        hou.parm('/obj/terrain/attribfrommap/filename').set(self.filepaths[0])
        hou.parm('/obj/terrain/attribfrommap/uv_invertv').set(1)
        n_attribFromMap.setInput(0, n_terrainGrid)

        # Create attribute wrangle node
        n_attrib_wrangle = n_terrain.createNode('attribwrangle', 'attribwrangle')
        hou.parm('/obj/terrain/attribwrangle/class').set(1)
        terrainAttribWrangleVEXpression = loadVexString('/Users/natashadaas/houdiniCapstone/terrainAttribWrangleVEXpression.txt')
        hou.parm('/obj/terrain/attribwrangle/snippet').set(terrainAttribWrangleVEXpression)

        hou.node('/obj/terrain/attribfrommap').setDisplayFlag(True)


def loadVexString(filename):
    with open(filename, 'r') as file:
        return file.read()


win = MyWidget()
win.show()
