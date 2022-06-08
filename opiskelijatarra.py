# APPLICATION FOR PRINTING STUDENT STICKERS

# Libraries and modules
# ---------------------

from PyQt5 import QtWidgets, uic, QtPrintSupport # UI elements, ui builder, and printing tools
from PyQt5.QtGui import QPainter, QTransform, QPixmap # For printing, scaling, and showing pictures
import json
import os # For path processing
import sys # For accessing system parameters
import code128Bcode # For creating barcodes with Libre Code 128

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
        self.horizontalShift = 120
        self.verticalShift = 160

        
        # CONTROLS
        self.firstNameInput = self.studentFirstNameLineEdit # Direct assign
        self.lastNameInput = self.findChild(QtWidgets.QLineEdit,'studentLastNameLineEdit') # Pointer assignment
        self.numberInput = self.studentNumberLineEdit
        self.horizontalMove = self.moveHorizontalSlider
        self.verticalMove = self.moveVerticalSlider
        self.scale = self.sizeDial

        # Settings controls
        self.placeholderPath = self.settingsPicturePathLineEdit

        # Read initial values from settings file
        self.settingsFile = open('studentSticker.settings', 'r',)
        self.settings = json.load(self.settingsFile)
        placeholderName = self.settings['placeholderName']
        self.placeholderPath.setText(placeholderName)
        self.settingsFile.close()

        # Initialise controls
        self.scale.setValue(self.scaleFactor)

        
        # INDICATORS
        self.nameOutput = self.stickerNameLabel
        self.nameOutput.setText('') # Clear it before use
        self.studentNumberOutput = self.stickerStudentNumberLabel
        self.studentNumberOutput.setText('')
        self.studentPhoto = self.pictureLabel
        self.scaleIndicator = self.scaleValueLabel

        # Initialise indicators
        self.scaleIndicator.setText(str(self.scaleFactor))

        # TODO: Disable print button until all fields are populated.


        # SIGNALS

        # Print the sticker
        self.printPushButton.clicked.connect(self.printSticker)

        # Load the picture of the student
        self.addPicturePushButton.clicked.connect(self.loadPicture)

        # signals for updating the student name
        self.firstNameInput.textChanged.connect(self.createFullName)
        self.lastNameInput.textChanged.connect(self.createFullName)

        # Signal when student number has been changed
        self.numberInput.textChanged.connect(self.updateBarcode)

        # Signal when scale changes
        self.scale.valueChanged.connect(self.updatePicture)

        # Save settings to a json file
        self.saveSettingsPushButton.clicked.connect(self.saveSettings)


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


    # Open a file dialog to choose a picture and place it to label
    def loadPicture(self):

        # Define what is the working directory
        relativeWorkingDirectory = '\Pictures'
        userProfilePath = os.path.expanduser('~')
        absoluteWorkingDirectory = userProfilePath + relativeWorkingDirectory

        # Create a file dialog
        fileName, check = QtWidgets.QFileDialog.getOpenFileName(
            None,
            'Valitse kuva',
            absoluteWorkingDirectory,
            'Kuvatiedostot (*.jpg *.png)',
        )
        
        # If user selects a file, create a pixmap
        if fileName:
            self.rawPhoto = QPixmap(fileName)
            self.studentPhoto.setPixmap(self.rawPhoto)


    # Concatenates first and last name and updates the sticker
    def createFullName(self):
        self.fullName = self.firstNameInput.text() + ' ' + self.lastNameInput.text()
        self.nameOutput.setText(self.fullName)


    # Creates a barcode from the student number
    def updateBarcode(self):
        bcode = code128Bcode.string2barcode(self.numberInput.text())
        self.studentNumberOutput.setText(bcode)

    # Resize and move the picture in the picture label
    def updatePicture(self):
        # Transform to fit the picture in the label
        self.scaleFactor = self.scale.value()
        transformation = QTransform() # Create transformation object
        scaleFactor = self.scaleFactor / 100
        transformation.scale(scaleFactor, scaleFactor) # Set the scale according to scalefactror
        # TODO: Make tools for moving the picture
        adjustedPhoto = self.rawPhoto.transformed(transformation) # Apply the transformation to the sticker
        self.studentPhoto.setPixmap(adjustedPhoto)


    def saveSettings(self):
        settingsFile = open('studentSticker.settings', 'w',)
        self.settings['placeholderName'] = self.placeholderPath.text()
        json.dump(self.settings, settingsFile)
        settingsFile.close()
        

if __name__ == '__main__':

    # Create the app
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = Ui()

    # Run the app
    app.exec_()