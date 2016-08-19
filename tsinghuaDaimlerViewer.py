#!/usr/bin/python
#   ----------------------
#   The Tsinghua-Daimler Cyclist Benchmark
#   ----------------------
#
#
#   License agreement
#-  ----------------
#
#   This dataset is made freely available for non-commercial purposes such as academic research, teaching, scientific publications, or personal experimentation. Permission is granted to use, copy, and distribute the data given that you agree:
#   1. That the dataset comes "AS IS", without express or implied warranty. Although every effort has been made to ensure accuracy, Daimler (or the website host) does not accept any responsibility for errors or omissions.
#   2. That you include a reference to the above publication in any published work that makes use of the dataset.
#   3. That if you have altered the content of the dataset or created derivative work, prominent notices are made so that any recipients know that they are not receiving the original data.
#   4. That you may not use or distribute the dataset or any derivative work for commercial purposes as, for example, licensing or selling the data, or using the data with a purpose to procure a commercial gain.
#   5. That this original license notice is retained with all copies or derivatives of the dataset.
#   6. That all rights not expressly granted to you are reserved by Daimler. 
#
#   Contact
#   -------
#
#   Fabian Flohr
#   mail: tdcb at fabian-flohr.de



#################
## Import modules
#################

# pyqt for everything graphical
from PyQt4 import QtGui, QtCore
# get command line parameters
import sys
# walk directories
import glob
# access to OS functionality
import os
# call processes
import subprocess
# copy things
import copy
from collections import namedtuple

import numpy as np

os.environ["QT_X11_NO_MITSHM"] = "1"

#################
## Helper classes
#################

# annotation helper
sys.path.append( os.path.normpath( os.path.join( os.path.dirname( __file__ ) , '..' , 'helpers' ) ) )
from annotation import Annotation


# a label and all meta information
Label = namedtuple( 'Label' , ['name'        , 'color'       , ] )
labels = [
    #       name                      color
    Label(  'unlabeled'          ,  (  0,    0,  0)),
    Label(  'pedestrian'         ,  (100,   20, 60)),
    Label(  'cyclist'            ,  (100,  80,  120)),
    Label(  'motorcyclist'       ,  (100,  169,  200)),
    Label(  'tricyclist'         ,  (100,  20,  255)),
    Label(  'wheelchairuser'     ,  (100,  80,  0)),
    Label(  'mopedrider'         ,  (100,  160,  60)),
]


# args.validLabels = ['pedestrian','cyclist','motorcyclist','tricyclist','wheelchairuser', 'mopedrider']

name2label      = { label.name    : label for label in labels           }



dataRootPath = "../"



#################
## Main GUI class
#################

# The main class which is a QtGui -> Main Window
class TsinhuaDaimlerViewer(QtGui.QMainWindow):

    #############################
    ## Construction / Destruction
    #############################

    # Constructor
    def __init__(self):
        # Construct base class
        super(TsinhuaDaimlerViewer, self).__init__()

        # This is the configuration.



        # The filename of the image we currently working on
        self.currentFile       = ""
        # The filename of the labels we currently working on
        self.currentLabelFile  = ""
        # Folder name of the dataset
        self.datasetFolderName              = ""
	# Folder name of the dataset
	self.disparityFolderName            = ""
        # The name of the currently loaded datasetType
        self.datasetType          = ""
        # The path of the labels.
        # Within these folders folder we expect the label with a filename matching
        # the images, except for the extension
        self.labelPath         = dataRootPath + "/labelData/"
        # The transparency of the labels over the image
        self.transp            = 0.5
        # The zoom toggle
        self.zoom              = False
        # The zoom factor
        self.zoomFactor        = 1.5
        # The size of the zoom window. Currently there is no setter or getter for that
        self.zoomSize          = 400 #px


        self.disp8bitToggle    = False

        # The width that we actually use to show the image
        self.w                 = 0
        # The height that we actually use to show the image
        self.h                 = 0
        # The horizontal offset where we start drawing within the widget
        self.xoff              = 0
        # The vertical offset where we start drawing withing the widget
        self.yoff              = 0
        # A gap that we  leave around the image as little border
        self.bordergap         = 20
        # The scale that was used, ie
        # self.w = self.scale * self.image.width()
        # self.h = self.scale * self.image.height()
        self.scale             = 1.0
        # Filenames of all images in current folder
        self.images            = []
        # Image extension
        self.imageExt          = "_leftImg8bit.png"
        self.dispExt          = "_disparity.png"
        self.gtExt             = "_labelData.json"
        # Current image as QImage
        self.image             = QtGui.QImage()
        # Index of the current image
        self.idx               = 0
        # All annotated objects in current image, i.e. list of labelObject
        self.annotation        = []
        # The current object the mouse points to. It's index in self.labels
        self.mouseObj          = -1
        # The object that is highlighted and its label. An object instance
        self.highlightObj      = None
        self.highlightObjLabel = None
        # The position of the mouse
        self.mousePosOrig      = None
        # The position of the mouse scaled to label coordinates
        self.mousePosScaled    = None
        # If the mouse is outside of the image
        self.mouseOutsideImage = True
        # The position of the mouse upon enabling the zoom window
        self.mousePosOnZoom    = None
        # A list of toolbar actions that need an image
        self.actImage          = []
        # A list of toolbar actions that need an image that is not the first
        self.actImageNotFirst  = []
        # A list of toolbar actions that need an image that is not the last
        self.actImageNotLast   = []
        # Toggle status of the play icon
        self.playState         = False

        # Default label
        self.defaultLabel = 'pedestrian'
        # Last selected label
        self.lastLabel = self.defaultLabel

        # Setup the GUI
        self.initUI()

        # load it
        self.loadDataset()
        self.imageChanged()

    # Destructor
    def __del__(self):
        return

    # Construct everything GUI related. Called by constructor
    def initUI(self):
        # Create a toolbar
        self.toolbar = self.addToolBar('Tools')

        # Add the tool buttons
        iconDir = os.path.join( os.path.dirname(sys.argv[0]) , 'icons' )

        # Loading
        loadAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'open.png' )), '&Tools', self)
        loadAction.setShortcuts(['o'])
        self.setTip( loadAction, 'Open datset' )
        loadAction.triggered.connect( self.getDatasetTypeFromUser )
        self.toolbar.addAction(loadAction)

        # Open previous image
        backAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'back.png')), '&Tools', self)
        backAction.setShortcut('left')
        backAction.setStatusTip('Previous image')
        backAction.triggered.connect( self.prevImage )
        self.toolbar.addAction(backAction)
        self.actImageNotFirst.append(backAction)

        # Open next image
        nextAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'next.png')), '&Tools', self)
        nextAction.setShortcut('right')
        self.setTip( nextAction, 'Next image' )
        nextAction.triggered.connect( self.nextImage )
        self.toolbar.addAction(nextAction)
        self.actImageNotLast.append(nextAction)

        # Play
        playAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'play.png')), '&Tools', self)
        playAction.setShortcut(' ')
        playAction.setCheckable(True)
        playAction.setChecked(False)
        self.setTip( playAction, 'Play all images' )
        playAction.triggered.connect( self.playImages )
        self.toolbar.addAction(playAction)
        self.actImageNotLast.append(playAction)
        self.playAction = playAction

        # Select image
        selImageAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'shuffle.png' )), '&Tools', self)
        selImageAction.setShortcut('i')
        self.setTip( selImageAction, 'Select image' )
        selImageAction.triggered.connect( self.selectImage )
        self.toolbar.addAction(selImageAction)
        self.actImage.append(selImageAction)

        # Enable/disable zoom. Toggle button
        zoomAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'zoom.png' )), '&Tools', self)
        zoomAction.setShortcuts(['z'])
        zoomAction.setCheckable(True)
        zoomAction.setChecked(self.zoom)
        self.setTip( zoomAction, 'Enable/disable permanent zoom' )
        zoomAction.toggled.connect( self.zoomToggle )
        self.toolbar.addAction(zoomAction)
        self.actImage.append(zoomAction)

        # Decrease transparency
        minusAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'minus.png' )), '&Tools', self)
        minusAction.setShortcut('-')
        self.setTip( minusAction, 'Decrease transparency' )
        minusAction.triggered.connect( self.minus )
        self.toolbar.addAction(minusAction)

        # Increase transparency
        plusAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'plus.png' )), '&Tools', self)
        plusAction.setShortcut('+')
        self.setTip( plusAction, 'Increase transparency' )
        plusAction.triggered.connect( self.plus )
        self.toolbar.addAction(plusAction)

        # Display path to current image in message bar
        displayFilepathAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'filepath.png' )), '&Tools', self)
        displayFilepathAction.setShortcut('f')
        self.setTip( displayFilepathAction, 'Show path to current image' )
        displayFilepathAction.triggered.connect( self.displayFilepath )
        self.toolbar.addAction(displayFilepathAction)

        # Toggle disp/8bit view
        toggleDisp8bit = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'layer.png' )), '&Tools', self)
        toggleDisp8bit.setShortcut('d')
        self.setTip( toggleDisp8bit, 'Toggle between disparity and 8bit image' )
        toggleDisp8bit.triggered.connect( self.toggleDisp8bitImage )
        self.toolbar.addAction(toggleDisp8bit)

        # Display help message
        helpAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'comment.png' )), '&Tools', self)
        helpAction.setShortcut('h')
        self.setTip( helpAction, 'Help' )
        helpAction.triggered.connect( self.displayHelpMessage )
        self.toolbar.addAction(helpAction)

        # Close the application
        exitAction = QtGui.QAction(QtGui.QIcon( os.path.join( iconDir , 'exit.png' )), '&Tools', self)
        exitAction.setShortcuts(['Esc'])
        self.setTip( exitAction, 'Exit' )
        exitAction.triggered.connect( self.close )
        self.toolbar.addAction(exitAction)

        # The default text for the status bar
        self.defaultStatusbar = 'Ready'
        # Create a statusbar. Init with default
        self.statusBar().showMessage( self.defaultStatusbar )

        # Enable mouse move events
        self.setMouseTracking(True)
        self.toolbar.setMouseTracking(True)
        # Open in full screen
        #self.showFullScreen( )
        # Set a title
        self.applicationTitle = 'Tsinghua-Daimler Dataset Viewer v0.1'
        self.setWindowTitle(self.applicationTitle)
        self.displayHelpMessage()
        self.getDatasetTypeFromUser()
        # And show the application
        self.show()

    #############################
    ## Toolbar call-backs
    #############################

    # Switch to previous image in file list
    # Load the image
    # Load its labels
    # Update the mouse selection
    # View
    def prevImage(self):
        if not self.images:
            return
        if self.idx > 0:
            self.idx -= 1
            self.imageChanged()
        else:
            message = "Already at the first image"
            self.statusBar().showMessage(message)
        return

    # Switch to next image in file list
    # Load the image
    # Load its labels
    # Update the mouse selection
    # View
    def nextImage(self):
        if not self.images:
            return
        if self.idx < len(self.images)-1:
            self.idx += 1
            self.imageChanged()
        elif self.playState:
            self.playState = False
            self.playAction.setChecked(False)
        else:
            message = "Already at the last image"
            self.statusBar().showMessage(message)
        if self.playState:
            QtCore.QTimer.singleShot(0, self.nextImage)
        return

    # Play images, i.e. auto-switch to next image
    def playImages(self, status):
        self.playState = status
        if self.playState:
            QtCore.QTimer.singleShot(0, self.nextImage)


    # Switch to a selected image of the file list
    # Ask the user for an image
    # Load the image
    # Load its labels
    # Update the mouse selection
    # View
    def selectImage(self):
        if not self.images:
            return

        dlgTitle = "Select image to load"
        self.statusBar().showMessage(dlgTitle)
        items = QtCore.QStringList( [ os.path.basename(i) for i in self.images ] )
        (item, ok) = QtGui.QInputDialog.getItem(self, dlgTitle, "Image", items, self.idx, False)
        if (ok and item):
            idx = items.indexOf(item)
            if idx != self.idx:
                self.idx = idx
                self.imageChanged()
        else:
            # Restore the message
            self.statusBar().showMessage( self.defaultStatusbar )


    # Toggle zoom
    def zoomToggle(self, status):
        self.zoom = status
        if status :
            self.mousePosOnZoom = self.mousePosOrig
        self.update()


    # Increase label transparency
    def minus(self):
        self.transp = max(self.transp-0.1,0.0)
        self.update()


    def displayFilepath(self):
        self.statusBar().showMessage("Current image: {0}".format( self.currentFile ))
        self.update()


    def displayHelpMessage(self):

        message = \
        self.applicationTitle + "\n\n" +\
        "INSTRUCTIONS\n" +\
        " - select a dataset type from drop-down menu\n" +\
        " - browse images and labels using\n" +\
        "   the toolbar buttons or the controls below\n" +\
        "\n" +\
        "CONTROLS\n" +\
        " - select dataset type [o]\n" +\
        " - highlight objects [move mouse]\n" +\
        " - next image [left arrow]\n" +\
        " - previous image [right arrow]\n" +\
        " - toggle autoplay [space]\n" +\
        " - increase/decrease label transparency\n" +\
        "   [ctrl+mousewheel] or [+ / -]\n" +\
        " - open zoom window [z]\n" +\
        "       zoom in/out [mousewheel]\n" +\
        "       enlarge/shrink zoom window [shift+mousewheel]\n" +\
        " - select a specific image [i]\n" +\
        " - show path to image below [f]\n" +\
	" - toggle between colorImage/disparity [d]\n" +\
        " - exit viewer [esc]\n"

        QtGui.QMessageBox.about(self, "HELP!", message)
        self.update()


    # Decrease label transparency
    def plus(self):
        self.transp = min(self.transp+0.1,1.0)
        self.update()

    # Close the application
    def closeEvent(self,event):
         event.accept()

    def toggleDisp8bitImage(self):
        self.disp8bitToggle = not self.disp8bitToggle
        self.imageChanged()


    #############################
    ## Custom events
    #############################

    def imageChanged(self):
        # Load the first image
        self.loadImage()
        # Load its labels if available
        self.loadLabels()
        # Update the object the mouse points to
        self.updateMouseObject()
        # Update the GUI
        self.update()

    #############################
    ## File I/O
    #############################

    # Load the currently selected dataset type if possible
    def loadDataset(self):
        # Search for all *.pngs to get the image list
        self.images = []
        if os.path.isdir(self.datasetFolderName):
            self.images = glob.glob(self.datasetFolderName + '/*' + self.imageExt )
            self.images.sort()

        self.disparities = []
        if os.path.isdir(self.disparityFolderName):
            self.disparities = glob.glob(self.disparityFolderName + '/*' + self.dispExt )
            self.disparities.sort()

            if self.currentFile in self.images:
                self.idx = self.images.index(self.currentFile)
            else:
                self.idx = 0


    # Load the currently selected image
    # Does only load if not previously loaded
    # Does not refresh the GUI
    def loadImage(self):
        success = False
        message = self.defaultStatusbar
        if self.images:
            if (self.disp8bitToggle):
                filename = self.disparities[self.idx]
            else:
                filename = self.images[self.idx]

            filename = os.path.normpath( filename )
            if not self.image.isNull() and filename == self.currentFile:
                success = True
            else:
                self.image = QtGui.QImage(filename)
                if self.image.isNull():
                    message = "Failed to read image: {0}".format( filename )
  		    print(message)
		    sys.exit()
                else:
                    message = "Read image: {0}".format( filename )
                    self.currentFile = filename
                    success = True

                #filenameDisp = os.path.normpath( self.disparities[self.idx] )
                #self.filenameDisp = QtGui.QImage(filenameDisp)
                #if self.filenameDisp.isNull():
                #    message = "Failed to read image: {0}".format( filenameDisp )
		#   print(message)
		#    sys.exit()
                #else:
                #    message = "Read image: {0}".format( filenameDisp )



        # Update toolbar actions that need an image
        for act in self.actImage:
            act.setEnabled(success)
        for act in self.actImageNotFirst:
            act.setEnabled(success and self.idx > 0)
        for act in self.actImageNotLast:
            act.setEnabled(success and self.idx < len(self.images)-1)

        self.statusBar().showMessage(message)

    # Load the labels from file
    # Only loads if they exist
    # Otherwise the filename is stored and that's it
    def loadLabels(self):
        filename = self.getLabelFilename()
        if not filename:
            self.clearAnnotation()
            return

        # If we have everything and the filename did not change, then we are good
        if self.annotation and filename == self.currentLabelFile:
            return

        # Clear the current labels first
        self.clearAnnotation()

        try:
            self.annotation = Annotation()
            self.annotation.fromJsonFile(filename)
        except IOError as e:
            # This is the error if the file does not exist
            message = "Error parsing labels in {0}. Message: {1}".format( filename, e.strerror )
            self.statusBar().showMessage(message)

        # Remember the filename loaded
        self.currentLabelFile = filename

        # Remeber the status bar message to restore it later
        restoreMessage = self.statusBar().currentMessage()

        # Restore the message
        self.statusBar().showMessage( restoreMessage )


    #############################
    ## Drawing
    #############################

    # This method is called when redrawing everything
    # Can be manually triggered by self.update()
    # Note that there must not be any other self.update within this method
    # or any methods that are called within
    def paintEvent(self, event):
        # Create a QPainter that can perform draw actions within a widget or image
        qp = QtGui.QPainter()
        # Begin drawing in the application widget
        qp.begin(self)
        # Update scale
        self.updateScale(qp)
        # Determine the object ID to highlight
        self.getHighlightedObject(qp)
        # Draw the image first
        self.drawImage(qp)
        # Draw the labels on top
        overlay = self.drawLabels(qp)
        # Draw the label name next to the mouse
        self.drawLabelAtMouse(qp)
        # Draw the zoom
        self.drawZoom(qp, overlay)

        # Thats all drawing
        qp.end()

        # Forward the paint event
        QtGui.QMainWindow.paintEvent(self,event)

    # Update the scaling
    def updateScale(self, qp):
        if not self.image.width() or not self.image.height():
            return
        # Horizontal offset
        self.xoff  = self.bordergap
        # Vertical offset
        self.yoff  = self.toolbar.height()+self.bordergap
        # We want to make sure to keep the image aspect ratio and to make it fit within the widget
        # Without keeping the aspect ratio, each side of the image is scaled (multiplied) with
        sx = float(qp.device().width()  - 2*self.xoff) / self.image.width()
        sy = float(qp.device().height() - 2*self.yoff) / self.image.height()
        # To keep the aspect ratio while making sure it fits, we use the minimum of both scales
        # Remember the scale for later
        self.scale = min( sx , sy )
        # These are then the actual dimensions used
        self.w     = self.scale * self.image.width()
        self.h     = self.scale * self.image.height()

    # Determine the highlighted object for drawing
    def getHighlightedObject(self, qp):
        # This variable we want to fill
        self.highlightObj = None

        # Without labels we cannot do so
        if not self.annotation:
            return

        # If available its the selected object
        highlightObjId = -1
        # If not available but the polygon is empty or closed, its the mouse object
        if highlightObjId < 0 and not self.mouseOutsideImage:
            highlightObjId = self.mouseObj
        # Get the actual object that is highlighted
        if highlightObjId >= 0:
            self.highlightObj = self.annotation.getLinearObjects()[highlightObjId]
            self.highlightObjLabel = self.annotation.getLinearObjects()[highlightObjId].uniqueId

    # Draw the image in the given QPainter qp
    def drawImage(self, qp):
        # Return if no image available
        if self.image.isNull():
            return

        # Save the painters current setting to a stack
        qp.save()
        # Draw the image
        qp.drawImage(QtCore.QRect( self.xoff, self.yoff, self.w, self.h ), self.image)
        #qp.drawImage(QtCore.QRect( self.xoff + self.w/2, self.yoff, self.w/2, self.h/2 ), self.filenameDisp)
        # Restore the saved setting from the stack
        qp.restore()

    def getPolygon(self, obj):
        poly = QtGui.QPolygonF()
        point0 = QtCore.QPointF(obj.boundingBoxLabel.p0.x,obj.boundingBoxLabel.p0.y)
        point1 = QtCore.QPointF(obj.boundingBoxLabel.p1.x,obj.boundingBoxLabel.p0.y)
        point2 = QtCore.QPointF(obj.boundingBoxLabel.p1.x,obj.boundingBoxLabel.p1.y)
        point3 = QtCore.QPointF(obj.boundingBoxLabel.p0.x,obj.boundingBoxLabel.p1.y)
        poly.append( point0 )
        poly.append( point1 )
        poly.append( point2 )
        poly.append( point3 )
        return poly

    # Draw the labels in the given QPainter qp
    # optionally provide a list of labels to ignore
    def drawLabels(self, qp, ignore = []):
        if self.image.isNull() or self.w == 0 or self.h == 0:
            return
        if not self.annotation:
            return

        # The overlay is created in the viewing coordinates
        # This way, the drawing is more dense and the polygon edges are nicer
        # We create an image that is the overlay
        # Within this image we draw using another QPainter
        # Finally we use the real QPainter to overlay the overlay-image on what is drawn so far

        # The image that is used to draw the overlays
        overlay = QtGui.QImage( self.w, self.h, QtGui.QImage.Format_ARGB32_Premultiplied )
	
	#sanity check if image is loaded
	eng = overlay.paintEngine();
	if (not eng):
            return

        # delete all labels from previous frame
        overlay.fill( QtCore.Qt.transparent )

        # Create a new QPainter that draws in the overlay image
        qp2 = QtGui.QPainter()
        qp2.begin(overlay)

        # The color of the outlines
        qp2.setPen(QtGui.QColor('white'))
        # Draw all objects
        for obj in self.annotation.getLinearObjects():


            poly = self.getPolygon(obj)

            # Scale the polygon properly
            polyToDraw = poly * QtGui.QTransform.fromScale(self.scale,self.scale)

            # Default drawing
            # Color from color table, solid brush
            try:
                col   = QtGui.QColor( *name2label[obj.classId].color     )
            except:
                print obj.classId
                col = (0,0,0)

            brush = QtGui.QBrush( col, QtCore.Qt.SolidPattern )
            qp2.setBrush(brush)
            # Overwrite drawing if this is the highlighted object
            if self.highlightObj and obj == self.highlightObj:
                # First clear everything below of the polygon
                qp2.setCompositionMode( QtGui.QPainter.CompositionMode_Clear )
                qp2.drawPolygon( polyToDraw )
                qp2.setCompositionMode( QtGui.QPainter.CompositionMode_SourceOver )
                # Set the drawing to a special pattern
                brush = QtGui.QBrush(col,QtCore.Qt.DiagCrossPattern)
                qp2.setBrush(brush)

            qp2.drawPolygon( polyToDraw )

        # Draw outline of selected object dotted
        if self.highlightObj:
            brush = QtGui.QBrush(QtCore.Qt.NoBrush)
            qp2.setBrush(brush)
            qp2.setPen(QtCore.Qt.DashLine)
            polyToDraw = self.getPolygon(self.highlightObj) * QtGui.QTransform.fromScale(self.scale,self.scale)
            qp2.drawPolygon( polyToDraw )

        # End the drawing of the overlay
        qp2.end()
        # Save QPainter settings to stack
        qp.save()
        # Define transparency
        qp.setOpacity(self.transp)
        # Draw the overlay image
        qp.drawImage(self.xoff,self.yoff,overlay)
        # Restore settings
        qp.restore()

        return overlay


    # Draw the label name next to the mouse
    def drawLabelAtMouse(self, qp):
        # Nothing to do without a highlighted object
        if not self.highlightObj:
            return
        # Nothing to without a mouse position
        if not self.mousePosOrig:
            return

        # Save QPainter settings to stack
        qp.save()

        # That is the mouse positiong
        mouse = self.mousePosOrig

        # Will show zoom
        showZoom = self.zoom and not self.image.isNull() and self.w and self.h

        # The text that is written next to the mouse
        mouseText = self.highlightObj.uniqueId

        # Where to write the text
        # Depends on the zoom (additional offset to mouse to make space for zoom?)
        # The location in the image (if we are at the top we want to write below of the mouse)
        off = 33
        if showZoom:
            off += self.zoomSize/2
        if mouse.y()-off > self.toolbar.height():
            top = mouse.y()-off
            btm = mouse.y()
            vAlign = QtCore.Qt.AlignTop
        else:
            # The height of the cursor
            if not showZoom:
                off += 20
            top = mouse.y()
            btm = mouse.y()+off
            vAlign = QtCore.Qt.AlignBottom

        # Here we can draw
        rect = QtCore.QRect()
        rect.setTopLeft(QtCore.QPoint(mouse.x()-200,top))
        rect.setBottomRight(QtCore.QPoint(mouse.x()+200,btm))

        # The font to use
        font = QtGui.QFont("Helvetica",20,QtGui.QFont.Bold)
        qp.setFont(font)
        # Non-transparent
        qp.setOpacity(1)
        # Draw the text, horizontally centered
#        qp.drawText(rect,QtCore.Qt.AlignHCenter|vAlign,mouseText)
        # Restore settings
        qp.restore()

    # Draw the zoom
    def drawZoom(self,qp,overlay):
        # Zoom disabled?
        if not self.zoom:
            return
        # No image
        if self.image.isNull() or not self.w or not self.h:
            return
        # No mouse
        if not self.mousePosOrig:
            return

        # Abbrevation for the zoom window size
        zoomSize = self.zoomSize
        # Abbrevation for the mouse position
        mouse = self.mousePosOrig

        # The pixel that is the zoom center
        pix = self.mousePosScaled
        # The size of the part of the image that is drawn in the zoom window
        selSize = zoomSize / ( self.zoomFactor * self.zoomFactor )
        # The selection window for the image
        sel  = QtCore.QRectF(pix.x()  -selSize/2 ,pix.y()  -selSize/2 ,selSize,selSize  )
        # The selection window for the widget
        view = QtCore.QRectF(mouse.x()-zoomSize/2,mouse.y()-zoomSize/2,zoomSize,zoomSize)
        if overlay :
            overlay_scaled = overlay.scaled(self.image.width(), self.image.height())
        else :
            overlay_scaled = QtGui.QImage( self.image.width(), self.image.height(), QtGui.QImage.Format_ARGB32_Premultiplied )

        # Show the zoom image
        qp.save()
        qp.drawImage(view,self.image,sel)
        qp.setOpacity(self.transp)
        qp.drawImage(view,overlay_scaled,sel)
        qp.restore()


    #############################
    ## Mouse/keyboard events
    #############################

    # Mouse moved
    # Need to save the mouse position
    # Need to drag a polygon point
    # Need to update the mouse selected object
    def mouseMoveEvent(self,event):
        if self.image.isNull() or self.w == 0 or self.h == 0:
            return

        mousePosOrig = QtCore.QPointF( event.x() , event.y() )
        mousePosScaled = QtCore.QPointF( float(mousePosOrig.x() - self.xoff) / self.scale , float(mousePosOrig.y() - self.yoff) / self.scale )
        mouseOutsideImage = not self.image.rect().contains( mousePosScaled.toPoint() )

        mousePosScaled.setX( max( mousePosScaled.x() , 0. ) )
        mousePosScaled.setY( max( mousePosScaled.y() , 0. ) )
        mousePosScaled.setX( min( mousePosScaled.x() , self.image.rect().right() ) )
        mousePosScaled.setY( min( mousePosScaled.y() , self.image.rect().bottom() ) )

        if not self.image.rect().contains( mousePosScaled.toPoint() ):
            print self.image.rect()
            print mousePosScaled.toPoint()
            self.mousePosScaled = None
            self.mousePosOrig = None
            self.updateMouseObject()
            self.update()
            return

        self.mousePosScaled    = mousePosScaled
        self.mousePosOrig      = mousePosOrig
        self.mouseOutsideImage = mouseOutsideImage

        # Redraw
        self.updateMouseObject()
        self.update()

    # Mouse left the widget
    def leaveEvent(self, event):
        self.mousePosOrig = None
        self.mousePosScaled = None
        self.mouseOutsideImage = True


    # Mouse wheel scrolled
    def wheelEvent(self, event):
        ctrlPressed = event.modifiers() & QtCore.Qt.ControlModifier

        deltaDegree = event.delta() / 8 # Rotation in degree
        deltaSteps  = deltaDegree / 15 # Usually one step on the mouse is 15 degrees

        if ctrlPressed:
            self.transp = max(min(self.transp+(deltaSteps*0.1),1.0),0.0)
            self.update()
        else:
            if self.zoom:
                # If shift is pressed, change zoom window size
                if event.modifiers() and QtCore.Qt.Key_Shift:
                    self.zoomSize += deltaSteps * 10
                    self.zoomSize = max( self.zoomSize, 10   )
                    self.zoomSize = min( self.zoomSize, 1000 )
                # Change zoom factor
                else:
                    self.zoomFactor += deltaSteps * 0.05
                    self.zoomFactor = max( self.zoomFactor, 0.1 )
                    self.zoomFactor = min( self.zoomFactor, 10 )
                self.update()


    #############################
    ## Little helper methods
    #############################

    # Helper method that sets tooltip and statustip
    # Provide an QAction and the tip text
    # This text is appended with a hotkeys and then assigned
    def setTip( self, action, tip ):
        tip += " (Hotkeys: '" + "', '".join([str(s.toString()) for s in action.shortcuts()]) + "')"
        action.setStatusTip(tip)
        action.setToolTip(tip)

    # Update the object that is selected by the current mouse curser
    def updateMouseObject(self):
        self.mouseObj   = -1
        if self.mousePosScaled is None:
            return
        for idx in reversed(range(len(self.annotation.getLinearObjects()))):
            obj = self.annotation.getLinearObjects()[idx]
            obj = self.annotation.getLinearObjects()[idx]
            if self.getPolygon(obj).containsPoint(self.mousePosScaled, QtCore.Qt.OddEvenFill):
                self.mouseObj = idx
                break

    # Clear the current labels
    def clearAnnotation(self):
        self.annotation = None
        self.currentLabelFile = ""

    def getDatasetTypeFromUser(self):
        # Reset the status bar to this message when leaving
        restoreMessage = self.statusBar().currentMessage()

        img_folder = os.path.join(dataRootPath, 'leftImg8bit')
        disp_folder = os.path.join(dataRootPath, 'disparity')
        label_folder = os.path.join(dataRootPath, 'labelData')
        labeled_cities = []
        data_dirs = ['valid', 'train', 'test', 'NonVRU']
        for d in data_dirs:
            cities = glob.glob(os.path.join(img_folder, d, '*'))
            cities.sort()
            labeled_cities.extend([(os.path.basename(c), d) for c in cities])

        # List of possible labels
        items = [d + ": " + c for (c,d) in labeled_cities]

        # Specify title
        dlgTitle = "Select dataset ['valid', 'train', 'test', 'NonVRU']"
        message  = dlgTitle
        question = dlgTitle
        message  = "Select dataset for viewing"
        question = "Which dataset would you like to view?"
        self.statusBar().showMessage(message)

        # Create and wait for dialog
        (datasetType, ok) = QtGui.QInputDialog.getItem(self, dlgTitle, question, items, 0, False)

        # Restore message
        self.statusBar().showMessage( restoreMessage )

        if ok and datasetType:
            self.datasetType = datasetType
            self.transp = 0.5
            self.datasetFolderName = os.path.normpath( os.path.join(img_folder, str(datasetType.split(": ")[0]), str(datasetType.split(": ")[1])) )
            self.disparityFolderName = os.path.normpath( os.path.join(disp_folder, str(datasetType.split(": ")[0]), str(datasetType.split(": ")[1])) )
            self.labelPath = os.path.normpath( os.path.join(label_folder, str(datasetType.split(": ")[0]), str(datasetType.split(": ")[1])) )
        self.loadDataset()
        self.imageChanged()

        return


    # Determine if the given candidate for a label path makes sense
    def isLabelPathValid(self,labelPath):
        return os.path.isdir(labelPath)

    # Get the filename where to load/save labels
    # Returns empty string if not possible
    # Set the createDirs to true, if you want to create needed directories
    def getLabelFilename( self , createDirs = False ):
        # We need the name of the current dataset selected
        if not self.datasetType:
            return ""
        # And we need to have a directory where labels should be searched
        if not self.labelPath:
            return ""
        # Without the name of the current images, there is also nothing we can do
        if not self.currentFile:
            return ""
        # Check if the label directory is valid. This folder is selected by the user
        # and thus expected to exist
        if not self.isLabelPathValid(self.labelPath):
            return ""

        # Folder where to store the labels
        labelDir = os.path.join( self.labelPath )

        # If the folder does not exist, create it if allowed
        if not os.path.isdir( labelDir ):
            if createDirs:
                os.makedirs( labelDir )
                if not os.path.isdir( labelDir ):
                    return ""
            else:
                return ""
        # Generate the filename of the label file
        filename = os.path.basename( self.currentFile )
        filename = filename.replace( self.dispExt, self.imageExt)
        filename = filename.replace( self.imageExt , self.gtExt )
        filename = os.path.join( labelDir , filename )
        filename = os.path.normpath(filename)
        return filename

    # Disable the popup menu on right click
    def createPopupMenu(self):
        pass


def main():

    app = QtGui.QApplication(sys.argv)
    tool = TsinhuaDaimlerViewer()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
