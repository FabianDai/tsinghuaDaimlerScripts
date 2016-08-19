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
import glob
import json
import re
import numpy as np
import matplotlib.pyplot as plt
import sys

class Evaluator():
    def __init__(self, gtFilePath):

        # ################################################
        # ######### CONFIGURATION ##########

        # If true, the script will produce additional output (caution: increased runtime)
        self.verbose = 0
        # Different difficulties can be selected (easy, moderate, hard). See the paper for further details
        self.difficulty = 'easy'
        # If true, other VRU ground truth boxes are used during the matching process, therefore other classes (e.g. motorcyclists)
        # which are detected and classified as the primary detection class (e.g. cyclist) do not cause a false positive
        self.ignoreOtherVRU = True  # if true other VRUs (see toleratedOtherClasses) are marked with the ignored flag, otherwise they are discarded

        # ################################################



        # ################################################
        # ######### CONFIGURATION ##########

        # path to the directory containing all gt json-files
        self.pathToGtFiles = gtFilePath
        # path to the directory containing all det json-files
        self.pathToDetFiles = None
        # extension of the gt json-files
        self.gtExt = "_labelData.json"
        # extension of the det json-files
        self.detExt = "_detection.json"

        # gt and det lists of the current frame
        self.detList = list()
        self.gtList = list()

        # gt and det lists over the whole dataset
        self.detListAll = list()
        self.gtListAll = list()

        # name of the currently processed frame/file
        self.currentDetFile = None
        self.currentGtFile = None
        # idx to the currently processed frame
        self.currentDetFileIdx = -1
        self.currentGtFileIdx = -1
        # list of all gt files
        self.gtFiles = list()
        # list of all det files
        self.detFiles = list()

        # ################################################
        # ######### DO NOT EDIT BELOW THIS LINE ##########
        # #################################################################################################
        # If you change any of this setting the calculated results wont be comparable to the results provided in our paper

        # Selected type on which the evaluation is performed (i.e: detector of this type is evaluated)
        self.detectionsType = 'cyclist'
        # Other classes which are tolerated, if the self.ignoreOtherVRU flag is set to one
        self.toleratedOtherClasses = ['pedestrian', 'bike', 'motorcyclist', 'tricyclist', 'wheelchairuser', 'mopedrider']
        # Minimal intersection over union between a ground truth bb and a detection bb to establish the match
        self.minIoU = 0.5
        # If no detection score is specified by the given detection, this value is used instead
        self.initScore = 1.0
        # If true, one ground truth annotation can be matched with multiple detections
        self.allowMultipleMatches = False
        # reference points used to calculate the average precision
        self.referencePoints = np.linspace(0, 1, 11) # 0, 0.1, ..., 1.0
        self.referencePoints.sort() # expect reference points to be sorted ascending


    # Load the currently selected dataset (given by gtFilePath and detFilePath)
    def loadDataset(self):
        self.clear()

        self.gtFiles = []
        self.detFiles = []

        # Load all ground truth files
        if os.path.isdir(self.pathToGtFiles) and len(self.gtFiles) <= 0:
            # Search for all *.json to get the file list
            self.gtFiles = glob.glob(self.pathToGtFiles + '/*' + self.gtExt )
            self.gtFiles.sort()
            self.currentGtFileIdx = 0

            # check if empty
            if len(self.gtFiles) == 0:
                print "ERROR: No ground truth files found at given location! ABORT."
		print "Given path was: {} and gt ext looked for was {}".format(self.pathToGtFiles, self.gtExt)
                return 0
        else:
            print "ERROR: Not a vaild ground truth path."
            print "Given path was: " + self.pathToGtFiles
            return 0

        # Load all detection files at given location
        if os.path.isdir(self.pathToDetFiles):
            # Search for all *.json to get the file list
            self.detFiles = glob.glob(self.pathToDetFiles + '/*' + self.detExt)
            self.detFiles.sort()
            self.currentDetFileIdx = 0

            # check if empty
            if len(self.detFiles) == 0:
                print "ERROR: No detection files found at given location! ABORT."
                print "Given path was: {} and dt ext looked for was {}".format(self.pathToDetFiles, self.detExt)
                return 0
        else:
            print "ERROR: Not a vaild detection path."
            print "Given path was: " + self.pathToDetFiles
            return 0

        if (len(self.detFiles) != len(self.gtFiles)):
            print "ERROR: Number of detection json files does not match the number of ground truth json files."
            print "Please provide for each image in the ground truth set one detection file in the format tsinghuaDaimlerDataset_{seq:0>6}_{frame:0>9}_{self.detExt}."
            return 0

        return 1


    def loadFrame(self):
        # get current det and gt filename
        detFilePath = self.detFiles[self.currentDetFileIdx]
        gtFilePath = self.gtFiles[self.currentGtFileIdx]

        # Check Data
        if not os.path.isfile(gtFilePath):
            print 'Given groundtruth json file not found: {}'.format(gtFilePath)
            return
        if not os.path.isfile(detFilePath):
            print 'Given detection json file not found: {}'.format(detFilePath)
            return
        dFile = os.path.basename(detFilePath)
        gFile = os.path.basename(gtFilePath)
        dFrameId = re.search('(.*?)' + self.detExt, dFile).group(1)
        gFrameId = re.search('(.*?)' + self.gtExt, gFile).group(1)
        if gFrameId != dFrameId:
            print 'Error: Frame identifier do not match. Check number and order of files in groundtruth and detection folder. Abort current frame.'
            if dFrameId > gFrameId:
                self.currentGtFileIdx +=1
            else:
                self.currentDetFileIdx += 1
            return 0


        # read annotation (gt) json file
        with open(gtFilePath, 'r') as f:
            jsonGtText = f.read()

        # get each annotation from current json file
        jsonDict = json.loads(jsonGtText)
        self.gtList = []
        for gtIn in jsonDict[ 'children' ]:
            type = gtIn['identity']
            h = gtIn['maxrow'] - gtIn['minrow']
            w = gtIn['maxcol'] - gtIn['mincol']

            # set ignore flag
            if type == self.detectionsType:
                ignore = 0
            elif self.ignoreOtherVRU and type in self.toleratedOtherClasses:
                ignore = 1
            elif h < 30 or "occluded>80" in gtIn['tags']:
                # Do not skip detections, which are to small or occluded
                ignore = 1
            else:
                # dont use this annotation
                continue

            # determine if current gt is within difficulty, otherwise set ignore
            if h < 30 or "occluded>80" in gtIn['tags']:
                # either smaller than 30px or occluded more than half of the object -> ignore = 1
                ignore = 1
            elif self.difficulty != "hard" and (h < 45 or "occluded>40" in gtIn['tags']):
                # mod, but gt h < 45 or occluded more than 10
                ignore = 1
            elif self.difficulty != "hard" and self.difficulty != "moderate" and (h < 60 or "occluded>10" in gtIn['tags']):
                # easy, but gt h < 60 or occluded
                ignore = 1

            gt = {
                'x': gtIn['mincol'],
                'y': gtIn['minrow'],
                'w': w,
                'h': h,
                'type': type,
                'ignore': ignore,
                'matched': 0,       # used during the evaluation
            }
            self.gtList.append(gt)


        # read detection json file
        with open(detFilePath, 'r') as f:
            jsonDetText = f.read()

        # save each detection from current json file
        jsonDict = json.loads(jsonDetText)
        self.detList = []
        for detIn in jsonDict[ 'children' ]:

            if 'score' in detIn:
                score = detIn['score']
            else:
                score = self.initScore

            det = {
                'x': detIn['mincol'],
                'y': detIn['minrow'],
                'w': detIn['maxcol'] - detIn['mincol'],
                'h': detIn['maxrow'] - detIn['minrow'],
                'type': detIn['identity'],
                'score': score,
                'matched': 0,       # used during the evaluation
            }
	     
            # we only accept detections of type detectionsType (here only "cyclist"). All other detections are ignored
	    if detIn['identity'] == self.detectionsType:
                self.detList.append(det)

        self.currentDetFile = dFrameId
        self.currentGtFile = gFrameId

        if self.verbose > 0:
            print "Loaded data for frame: {}".format(self.currentDetFile)
        # increment idx
        self.currentGtFileIdx += 1
        self.currentDetFileIdx += 1
        return 1


    def evaluateFrame(self):

        # sort det lists by detection score desc
        self.detList.sort(key=lambda k: k['score'], reverse=True)

        # sort gt_list by ignore flag (ignored gt at the end of the list)
        self.gtList.sort(key=lambda k: k['ignore'])

        # iterate over all detections (sorted by score) and find best matching gt (highest IoU)
        for det in self.detList:
            maxIoU = self.minIoU
            idxBestGt = -1
            matchedWithIgnore = False

            # iterate over all gt annotations
            for idx_gt, gt in enumerate(self.gtList):
                matchedGt = gt['matched']

                # if gt is allready matched, and no multiple matches are allowed: next gt
                if matchedGt and not self.allowMultipleMatches and not gt['ignore']:
                    continue

                # if det is matched with a non ignoreable gt and current gt is ignorable: next det (due to the sorting only ignor-gts follow)
                if idxBestGt >= 0 and not matchedWithIgnore and gt['ignore']:
                    break

                # calculate IoU of gt and det
                cIoU = self.calcIoU(gt, det)

                # smaller than maximum so far: continue
                if cIoU < maxIoU:
                    continue
                else:
                    maxIoU = cIoU
                    idxBestGt = idx_gt

                    if gt['ignore']:
                        matchedWithIgnore = True

            # Write match back to det
            if idxBestGt >= 0:
                if matchedWithIgnore:
                    det['matched'] = -1
                else:
                    det['matched'] = 1

            # Write match back to gt
            if idxBestGt >= 0:
                self.gtList[idxBestGt]['matched'] = 1

        # extend det and gt lists
        self.detListAll.extend(self.detList)
        self.gtListAll.extend(self.gtList)

    def calcIoU(self, gt, det):
        # Calculates the intersection over union of the given gt and det bbs
        iou = 0

        # calculate height and width of intersecting area
        w_inter = float(min(gt['w'] + gt['x'], det['w'] + det['x']) - max(gt['x'], det['x']))
        h_inter = float(min(gt['h'] + gt['y'], det['h'] + det['y']) - max(gt['y'], det['y']))

        if (w_inter <= 0 or h_inter <= 0):
            return 0

        # calculate area (intersection and union)
        area_I = w_inter * h_inter
        if gt['ignore']:
            area_U = det['w'] * det['h']
        else:
            area_U = (det['w'] * det['h']) + (gt['w'] * gt['h']) - area_I

        iou = area_I / area_U
        return iou

    def calcPR(self):

        # remove all ignored gt
        self.gtListAll[:] = [g for g in self.gtListAll if g.get('ignore') == False]

        # remove all det matched with an ignored gt
        self.detListAll[:] = [d for d in self.detListAll if d.get('matched') != -1]

        # Check for empty lists
        if len(self.detListAll) <= 0:
            print "ERROR. No valid detections present for evaluation. ABORT."
            return 0,0,0
        if len(self.gtListAll) <= 0:
            print "ERROR. No valid ground truth objects present for evaluation. ABORT."
            return 0,0,0

        # sort detections desc by their detection score
        self.detListAll.sort(key=lambda k: k['score'], reverse=True)

        # cumsum falsepositive and truepositive
        fp = np.zeros(len(self.detListAll))
        tp = np.zeros(len(self.detListAll))
        tp_cnt = 0
        fp_cnt = 0

        for idxDet, det in enumerate(self.detListAll):
            if det['matched'] == 1:
                # increase tp
                tp_cnt += 1
            elif det['matched'] == 0:
                # increase fp
                fp_cnt += 1

            fp[idxDet] = fp_cnt
            tp[idxDet] = tp_cnt

        # number of positive cases (gt)
        nof_pos = len(self.gtListAll)

        # calculate the x and y data points of the PR-curve
        x_points = np.divide(tp, nof_pos)
        y_points = np.divide(tp, np.add(tp, fp))

        # calculate the precision at each reference point
        ref_pts = np.zeros(len(self.referencePoints))
        idxR = 0
        ref = self.referencePoints[idxR]
        for idxDet, rec in enumerate(x_points):
            if rec >= ref:
                ref_pts[idxR] = y_points[idxDet]
                idxR += 1
                if idxR >= len(self.referencePoints):
                    break;

                ref = self.referencePoints[idxR]
                continue

        avg_prec = np.mean(ref_pts)

        return x_points, y_points, avg_prec

    def clear(self):
        # Clear after run
        self.gtListAll = list()
        self.detListAll = list()

    # starts the evaluation process, main loop
    def run(self, detectionEvalList):

        # Iterate over each given set of detections
        for detTuple in detectionEvalList:
            curDetMethodName = detTuple[0]
            self.pathToDetFiles = detTuple[1]
            lineColor = None

            if self.verbose == 1:
                print 'Start evaluation for {}'.format(curDetMethodName)

            # process each set of detections one time with and without ignoring other VRUs
            for ignoreFlag in [1, 0]:
                # get fileLists for gt and det
                self.ignoreOtherVRU = ignoreFlag

                bValidDataSet = self.loadDataset()
                # check DataSet
                if bValidDataSet != 1:
                    print "Cancel evaluation process. Please check the content of your selected annotation and detection folders. One .json-file per frame. Same number of frames required."
                    return
                nSkippedFrames = 0
                nProcessedFrames = 0

                # process each frame
                while(self.currentGtFileIdx < len(self.gtFiles)):

                    # load current frame data (gt and det)
                    bValid = self.loadFrame()

                    if bValid == 0:
                        if self.verbose == 1:
                            print 'Skip current frame due to errors.'
                        nSkippedFrames += 1
                        continue

                    # process current frame, calculate matches
                    self.evaluateFrame()

                    nProcessedFrames += 1

                # calculate precision-recall values
                x_points, y_points, avg_prec = self.calcPR()

                # check for error
                if len(x_points) <= 1 and x_points == 0 and y_points == 0 and avg_prec == 0:
                    return 0

                # plot the calculated PR-graph
                if self.ignoreOtherVRU:
                    line, = plt.plot(x_points, y_points, linewidth=2)
                    line.set_label(curDetMethodName +': {0:.3f}'.format(avg_prec) + ' ignore')
                    lineColor = plt.get(line, 'color')
                else:
                    line, = plt.plot(x_points, y_points, '--', linewidth=2, color=lineColor)
                    line.set_label(curDetMethodName + ': {0:.3f}'.format(avg_prec) + ' discard')

                print '#########################'
                print 'Finished evaluation of ' + curDetMethodName + '\n'
                print 'Avg prec: ', avg_prec
                print 'Processed number of frames: ', nProcessedFrames
                print 'Skipped ', nSkippedFrames, ' Frames'
                print '#########################\n'

        # return
        return 1








#########################################################################
# entry point of evaluation script

# Path to the ground truth files, e.g: ../labelData/test/tsinghuaDaimlerDataset
pathToGtFiles = '../labelData/test/tsinghuaDaimlerDataset/'
#pathToGtFiles = '../labelData/test/tsinghuaDaimlerDataset'

# Save location of the resulting figure
pathToFigSaveLoc = '/tmp/resultsFig.png'

# Create list of all different detection results, containing the name of the used detections method along with the path of the generated .json-files
detectionEvalList = list()
detectionEvalList.append(('ACF', '../detection'))
#detectionEvalList.append(('LDCF', '[YOUR_ALGO_PATH]/cyclist_gt+dt_LDCF'))
#detectionEvalList.append(('VGG16_SP', '[YOUR_ALGO_PATH]/cyclist_gt+dt_VGG16_SP_test'))

# Create Evaluator object with path to ground truth data
eval = Evaluator(pathToGtFiles)


bValid = eval.run(detectionEvalList)

if bValid > 0:
    plt.axis([0.0, 1, 0.0, 1])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Tsinghua Daimler Evaluation Results [' + eval.difficulty + ']')
    plt.legend()

    plt.savefig(pathToFigSaveLoc)
    print "Saved resulting figure to: " + pathToFigSaveLoc

    plt.show(block=True)

    sys.exit(0)

