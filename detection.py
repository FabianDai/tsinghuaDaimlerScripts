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


import os
import json
from collections import namedtuple
from annotation import JsonFrameObject


# A single detection/object, using the same python layout as the json object
class JsonDetObject:
    def __init__(self):
        self.minrow = 0
        self.maxrow = 0
        self.mincol = 0
        self.maxcol = 0
        self.score = 0          # string

        self.identity = "None"    # string, class informationen, e.g. "pedestrian"
        self.trackid = "None"     # string
        self.tags = list()       # list of strings, e.g. "occluded>10"

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def fromJsonText(self, jsonText):
        # position data of the bounding box
        self.mincol = int(jsonText['mincol'])
        self.minrow = int(jsonText['minrow'])
        self.maxcol = int(jsonText['maxcol'])
        self.maxrow = int(jsonText['maxrow'])

        # detection score (float)
        self.score = float(jsonText['score'])

        # class type (str)
        self.identity = str(jsonText['identity'])

        # track identifer, class type followed by track id e.g. Pedestrian_1 (str)
        self.trackid = str(jsonText['trackid'])

        # occlusion flag and other tags:
        self.tags = jsonText['tags']



# The detections of a whole image
class Detection:
    # Constructor
    def __init__(self, imgName):
        # the width of that image and thus of the label image
        self.imgWidth  = 2048
        # the height of that image and thus of the label image
        self.imgHeight = 1024
        # the list of objects
        self.objects = []
        # the name of the image (identifier)
        self.imgName = imgName

    def addDetAnnotation(self, minrow, mincol, maxrow, maxcol, score, identity, trackid="None"):
        # create new detection object
        newDet = JsonDetObject()

        newDet.mincol = mincol
        newDet.minrow = minrow
        newDet.maxcol = maxcol
        newDet.maxrow = maxrow

        newDet.identity = identity

        newDet.trackid = trackid
        newDet.score = score

        # save object to list of current annotations
        self.objects.append(newDet)

    def toJsonText(self):
        jsonFrameObj = JsonFrameObject()
        jsonFrameObj.imgname = self.imgName

        jsonFrameObj.children.extend(self.objects)

        return json.dumps(jsonFrameObj, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def toJsonFile(self, jsonFile):
        # Save current frame with all annotations as jsonFile

        with open(jsonFile, 'w') as f:
            json.dump(self, f, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def fromJsonText(self, jsonText):
        jsonDict = json.loads(jsonText)
        self.objects   = []
        for objIn in jsonDict[ 'children' ]:
            obj = JsonDetObject()
            obj.fromJsonText(objIn)
            self.objects.append(obj)

    # Read a json formatted detection file and return all the included hypotheses
    def fromJsonFile(self, jsonFile):
        if not os.path.isfile(jsonFile):
            print 'Given json file not found: {}'.format(jsonFile)
            return
        with open(jsonFile, 'r') as f:
            jsonText = f.read()
            self.fromJsonText(jsonText)

    # return a list of all detection bounding boxes
    def getLinearObjects(self):
        allObjects = []
        allObjects.extend(self.objects)

        return allObjects

    # parse the imgName included in the groundtruth files into the right name scheme required by the evaluation script
    def createDetJsonFileNameFromImgName(self, imgNameFromGt):
        # e.g.:
        # FROM:     tsinghuaDaimlerDataset_2014-12-04_082614_000027014_leftImg8bit.png
        # TO:       tsinghuaDaimlerDataset_2014-12-04_082614_000027014_detections.json
        return str.replace(imgNameFromGt, '_leftImg8bit.png', '_detections.json')



if __name__ == "__main__":
    jsonFile = "./Detections_sample.json"
    det = Detection('tsinghuaDaimlerDataset_2014-12-04_082614_000027014_leftImg8bit.png')
    det.fromJsonFile(jsonFile)

    jsonText = det.toJsonText()
    print jsonText

    # add a new detection hypothesis, top left point (10,30), bottom right point (45,52),
    # with a detection score of 1.5 and the detected class "pedestrian" to the current frame
    det.addDetAnnotation(10, 30, 45, 52, 1.5, 'pedestrian')

    jsonText = det.toJsonText()
    print jsonText

    # export the current frame with all added detection and save as json-file at given path
    #det.toJsonFile("./tsinghuaDaimlerDataset_2014-12-04_082614_000027014_detections.json")

    testList = det.getLinearObjects()
