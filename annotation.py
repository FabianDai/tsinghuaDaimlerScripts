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

# A point in the polygon
Point = namedtuple('Point', ['x', 'y'])

class Box:
    def __init__(self, x0,y0,x1,y1):
        self.p0 = Point(x0,y0)
        self.p1 = Point(x1,y1)

# A single annotation/object, using the same python layout as the json object
class JsonGtObject:
    def __init__(self):
        self.minrow = 0
        self.maxrow = 0
        self.mincol = 0
        self.maxcol = 0

        self.identity = None    # string, class informationen, e.g. "pedestrian"
        self.trackid = None     # string
        self.uniqueId = None    # int
        self.tags = list()      # list of strings, e.g. "occluded>10"

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# One whole frame, including all annotations/objects
class JsonFrameObject:
    def __init__(self):
        self.imgname = None     # image name

        self.tags = list()      # list of strings
        self.children = list()  # list of JsonDetObjects



# A single annotated object
class CsObject:
    # Constructor
    def __init__(self):
        # the label
        self.boundingBoxLabel = Box(0,0,0,0)
        self.occluded = 0
        self.classId = None
        self.trackId = None
        self.uniqueId = None


    def fromJsonText(self, jsonText):

        # the bounding box label (Box)
        self.boundingBoxLabel   = Box(jsonText['mincol'],jsonText['minrow'],jsonText['maxcol'],jsonText['maxrow'])

        # class type (str)
        self.classId            = jsonText[ 'identity' ]

        # track identifer, class type followed by track id e.g. Pedestrian_1 (str)
        self.trackId            = jsonText[ 'trackid' ]

        # unique id for object (int)
        self.uniqueId           = jsonText[ 'uniqueid' ]

        # occlusion flag:
        #   0: no occlusion
        #   10: occlusion between 10%-30%
        #   30: occlusion between 30%-50%
        #   50: occlusion above 50%
        self.occluded           = 0
        if "occluded>10" in jsonText[ 'tags' ]:
            self.occluded = 10
        if "occluded>30" in jsonText[ 'tags' ]:
            self.occluded = 30
        if "occluded>50" in jsonText[ 'tags' ]:
            self.occluded = 50



# The annotation of a whole image
class Annotation:
    # Constructor
    def __init__(self, imgName=None):
        # the width of that image and thus of the label image
        self.imgWidth  = 2048
        # the height of that image and thus of the label image
        self.imgHeight = 1024
        # the list of objects
        self.objects = []
        # the name of the image (identifier)
        self.imgName = imgName

    def addGtAnnotation(self, minrow, mincol, maxrow, maxcol, identity, trackId=None, uniqueId = None):
        # create new annotation object
        newObj = CsObject()

        newObj.boundingBoxLabel = Box(mincol, minrow, maxcol, maxrow)
        newObj.classId = identity

        newObj.trackId = trackId
        newObj.uniqueId = uniqueId

        # save object to list of current annotations
        self.objects.append(newObj)



    def toJsonText(self):
        jsonFrameObj = JsonFrameObject()
        jsonFrameObj.imgname = self.imgName

        for obj in self.objects:
            jsonObj = JsonGtObject()
            jsonObj.identity = obj.classId
            jsonObj.trackid = obj.trackId
            jsonObj.uniqueId = obj.uniqueId

            jsonObj.mincol = obj.boundingBoxLabel.p0.x
            jsonObj.minrow = obj.boundingBoxLabel.p0.y
            jsonObj.maxcol = obj.boundingBoxLabel.p1.x
            jsonObj.maxrow = obj.boundingBoxLabel.p1.y

            if obj.occluded >= 50:
                jsonObj.tags.append("occluded>50")
            elif obj.occluded >= 30:
                jsonObj.tags.append("occluded>30")
            elif obj.occluded >=10:
                jsonObj.tags.append("occluded>10")

            # add current annotation/object to children list of the frame
            jsonFrameObj.children.append(jsonObj)

        return json.dumps(jsonFrameObj, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def toJsonFile(self, jsonFile):
        # Save current frame with all annotations as jsonFile

        with open(jsonFile, 'r') as f:
            json.dump(self, f, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def fromJsonText(self, jsonText):
        jsonDict = json.loads(jsonText)
        self.objects   = []
        for objIn in jsonDict[ 'children' ]:
            obj = CsObject()
            obj.fromJsonText(objIn)
            self.objects.append(obj)

    # Read a json formatted polygon file and return the annotation
    def fromJsonFile(self, jsonFile):
        if not os.path.isfile(jsonFile):
            print 'Given json file not found: {}'.format(jsonFile)
            return
        with open(jsonFile, 'r') as f:
            jsonText = f.read()
            self.fromJsonText(jsonText)

    def getLinearObjects(self):
        allObjects = []
        allObjects.extend(self.objects)
        for rootObject in self.objects:
            allObjects.append(rootObject)

        return allObjects



if __name__ == "__main__":
    jsonFile = "./GroundTruthAnnotations_sample.json"
    annot = Annotation()
    annot.fromJsonFile(jsonFile)

    jsonText = annot.toJsonText()
    print jsonText
