# APPLICATION FOR PRINTING STUDENT STICKERS

# Libraries and modules
# ---------------------

from PyQt5 import QtWidgets, uic, QtPrintSupport # UI elements, ui builder and printing tools
from PyQt5.QtGui import QPainter, QTransform, QPixmap # For printing, scaling and showing pictures
from PyQt5.QtCore import Qt # For pixmap scaling
import json # To read and write settings ins JSON format
import os # For path processing
import sys # For accessing system parameters
import code128Bcode # For creating barcodes with Libre Code 128 font

# Class definitions
# -----------------

class Ui(QtWidgets.QMainWindow):

    # CONSTRUCTOR
    def __init__(self):
        super().__init__()

        # Load the UI definition file
        uic.loadUi('opiskelijatarra.ui', self)

        # DATA VALUES

        # Settings

        # Initial values
        self.rawPhoto = QPixmap('placeholder.png')
        self.scaleFactor = 100
        self.horizShift = 0
        self.vertShift = 0

        # CONTROLS
        self.firstNameInput = self.studentFirstNameLineEdit # Direct assignment
        self.lastNameInput = self.findChild(QtWidgets.QLineEdit,'studentLastNameLineEdit') # Pointer assignment
        self.numberInput = self.studentNumberLineEdit
        self.horizMove = self.moveHorizontalSlider
        self.vertMove = self.moveVerticalSlider
        self.scale = self.sizeDial

        # Settings controls
        self.pholderPath = self.settingsPicturePathLineEdit
        
        # Read initial values from settings file
        self.settingsFile = open('studentSticker.settings', 'r')
        self.settings = json.load(self.settingsFile) # load json data to dict
        placeholderName = self.settings['placeholderName'] # Read by key
        self.pholderPath.setText(placeholderName)
        self.settingsFile.close() # Close the file

        # Initialize controls
        self.scale.setValue(self.scaleFactor)

        # INDICATORS
        self.nameOutput = self.stickerNameLabel
        self.nameOutput.setText('') # Clear it before use
        self.studentNumberOutput = self.stickerStudentNumberLabel
        self.studentNumberOutput.setText('')
        self.studentPhoto = self.pictureLabel
        self.scaleIndicator = self.scaleValueLabel
        self.dimensions = self.pictureSizeLabel

        # Initalize indicators
        self.scaleIndicator.setText(str(self.scaleFactor) + '%')
        self.dimensions.setText('')
        
        # Disable print button until all fields are populated
        self.printPushButton.setEnabled(False)
        
        # SIGNALS

        # Print the sticker
        self.printPushButton.clicked.connect(self.printSticker)

        # Load the picture of the student
        self.addPicturePushButton.clicked.connect(self.loadPicture)

        # Signals for updating the student name
        self.firstNameInput.textChanged.connect(self.createFullName)
        self.lastNameInput.textChanged.connect(self.createFullName)

        # Signal when student number has been changed
        self.numberInput.textChanged.connect(self.updateBarcode)

        # Signal when scale dial or move slider values have been changed
        self.scale.valueChanged.connect(self.updatePicture)
        self.horizMove.valueChanged.connect(self.updatePicture)
        self.vertMove.valueChanged.connect(self.updatePicture)

        # Save settings to json file
        self.saveSettingPushButton.clicked.connect(self.saveSettings)
        # SHOW THE UI
        self.show()
    
    # SLOTS (Methods)

    # Print the sticker 
    def printSticker(self):

        # Create a printer object
        # printer = QtPrintSupport.QPrinter() # Screen Hard Copy

        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)

        # Create print dialog window object
        printDialog = QtPrintSupport.QPrintDialog(printer, self) # Screen Hard Copy



        # Check if user has not cancelled the dialog, attn Accepted with capital A
        if printDialog.exec_() == QtPrintSupport.QPrintDialog.Accepted:
            
            # Create a painter object to create printable area
            painter = QPainter()
            
            # Start printing process
            painter.begin(printer)

            # Define the area to be printed
            sticker = self.stickerFrame.grab()

            # Transform to high quality (300 dpi)
            transformation = QTransform() # Create transformation object
            transformation.scale(5, 5) # Set the scale to 5 x
            sticker = sticker.transformed(transformation) # Apply the transformation to the sticker

            # Print the area
            painter.drawPixmap(30, 30, sticker)

            # Close printer
            painter.end()

    # Open a file dialog to choose a file and place the picture to label
    def loadPicture(self):

        # Define what is the working directory
        relativeWorkingDirectory = '\Pictures'
        userProfilePath = os.path.expanduser('~')
        absoluteWorkingDirectory = userProfilePath + relativeWorkingDirectory

        # Create a file dialog
        fileName, check = QtWidgets.QFileDialog.getOpenFileName(None, 'Valitse kuva', absoluteWorkingDirectory, 'Kuvatiedostot (*.jpg *.png)')

        # If user selects a file create a pixmap
        if fileName:
            self.rawPhoto = QPixmap(fileName)
            self.studentPhoto.setPixmap(self.rawPhoto)

        # TODO: Must set sliders and dials to their initial values

    # Concatenates first and last name and updates the sticker
    def createFullName(self):
        self.fullName = self.firstNameInput.text() + ' ' + self.lastNameInput.text()
        self.nameOutput.setText(self.fullName)
        self.checkData()

    # Creates a barcode from the student number
    def updateBarcode(self):
        bcode = code128Bcode.string2barcode(self.numberInput.text())
        self.studentNumberOutput.setText(bcode)
        self.checkData()

    # Resize and move the picture in the picture label initial position is top left
    def updatePicture(self):

        # Get the original picture size with QPixmap methods
        rawPictureSize = self.rawPhoto.size() # Returns an object with 2 methods to fing dimensions
        rawWidth = rawPictureSize.width()
        rawHeight = rawPictureSize.height()

        # Cretate a scaled picture 10 to 100 % and use smooth transormation
        self.scaleFactor = self.scale.value() 
        scaleFactor = self.scaleFactor / 100
        self.scaledPhoto = self.rawPhoto.scaled(rawWidth * scaleFactor, rawHeight * scaleFactor, Qt.AspectRatioMode.IgnoreAspectRatio ,Qt.TransformationMode.SmoothTransformation)
        
        # Measure the size of the scaled picture
        scaledPictureSize =self.scaledPhoto.size() # Returns an object with 2 methods to fing dimensions
        scaledWidth = scaledPictureSize.width()
        scaledHeight = scaledPictureSize.height()

        # Set maximum values for sliders moving the picture
        self.horizMove.setMaximum(scaledWidth - 1)
        self.vertMove.setMaximum(scaledHeight - 1)

        # Read slider values and move the picture in the lablel accordingly by creating a copy
        hmstart = self.horizMove.value()
        vmstart = self.vertMove.value()
        finalPhoto = self.scaledPhoto.copy(hmstart, vmstart, scaledWidth - hmstart, scaledHeight -vmstart)
        self.studentPhoto.setPixmap(finalPhoto)

        # Show dimensions of the scaled image in the label
        dimensionsText = str(scaledWidth) + ' x ' + str(scaledHeight)
        self.dimensions.setText(dimensionsText)

    # Chechk if name fields and student number field are populated -> enable print button
    def checkData(self):
        fnameLength = len(self.firstNameInput.text())
        lnameLength = len(self.lastNameInput.text())
        numberLength = len(self.numberInput.text())
        allPopulated = fnameLength * lnameLength * numberLength
        if allPopulated > 0:
            self.printPushButton.setEnabled(True)
        else:
            self.printPushButton.setEnabled(False)
        
        

    # Save settings
    def saveSettings(self):
         settingsFile = open('studentSticker.settings', 'w') # Open json file for writing
         self.settings['placeholderName'] = self.pholderPath.text() # Change value by key
         json.dump(self.settings, settingsFile) # Write all settings back to file
         settingsFile.close() # Close the file

if __name__ == '__main__':

    # Create the app
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = Ui()

    # Run the app
    app.exec_()
