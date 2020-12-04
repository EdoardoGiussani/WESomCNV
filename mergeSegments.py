#!/usr/bin/env python3

import utility
import argparse
import statistics


def main():
    print('\nRunning mergeSegments.py\n')

    args = parseArgs()

    sTime = utility.startTime()

    armsDict = getArmsInfo(args.armRef)
    mergedSegs = getMergedSegments(args.inputFile, 
                                   armsDict, 
                                   args.maximum, 
                                   args.minimum)
    utility.writeOutput(mergedSegs, args.outputFile)

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = 'Merge segments from R output')

    parser.add_argument('inputFile', metavar='segmentFile', 
                        action='store', type=utility.existingFile,
                        help='')
    parser.add_argument('-o', '--output', dest='outputFile',
                        action='store', type=utility.existingFilePath, required=False, 
                        default=utility.workingDirectory() + '/output.merged.tsv',
                        help='')
    parser.add_argument('-r', '--ref-arm', dest='armRef',
                        action='store', type=utility.existingFile, required=False,
                        default=utility.programDirectory() + '/refs/armSize.tsv',
                        help='')
    parser.add_argument('-a', '--amp-threshold', dest='maximum',
                        action='store', type=float, required=False, 
                        default=0.25,  
                        help='')
    parser.add_argument('-d', '--del-threshold', dest='minimum',
                        action='store', type=float, required=False, 
                        default=-0.25, 
                        help='')

    args = parser.parse_args()
    utility.printParameters(args)
    return args


def getArmsInfo(armInputFile):
    headList = ['chrom', 'start', 'end', 'name']
    headInts = ['start', 'end']
    arms = {}      
    with open(armInputFile, 'r') as inFile:
        header = utility.lineToHeader(inFile.readline(), headList)

        for line in inFile:
            arm = utility.lineToDict(line, header, ints = headInts)
            arm['length'] = arm['end'] - arm['start']
            arm['name'] = arm['chrom'] + arm['name']

            if not arm['chrom'] in arms:
                arms[arm['chrom']] = {}
            arms[arm['chrom']][arm['name']] = arm
    return arms


def getMergedSegments(inputFile, armsDict, maximum, minimum):
    mergedSegs = []
    toMerge = []
    actualArm = ''
    actualType = ''
    
    with open(inputFile, 'r') as inFile:
        header = utility.lineToHeader(inFile.readline())

        for line in inFile:
            segment = utility.lineToDict(line, header)
            segment = addArm(segment, armsDict)
            segment = addEventType(segment, maximum, minimum)
            mergedSegs.append(segment)
    return mergedSegs

#            if segment['arm'] == actualArm and segment['type'] == actualType:
#                toMerge.append(segment)
#            else: 
#                if toMerge:
#                    mergedSegs.append(mergeSegments(toMerge, armsDict))
#                toMerge = [segment]
#                actualArm = segment['arm']
#                actualType =  segment['type']
#        mergedSegs.append(mergeSegments(toMerge, armsDict))
#    return mergedSegs


def mergeSegments(segs, armsDict):
    mySeg = segs[0]

    start = min(seg['start'] for seg in segs)
    end = max(seg['end'] for seg in segs)
    length = end - start

    if mySeg['chrom'] in armsDict:              #If not?
        arms = armsDict[mySeg['chrom']]
        chromLen = max(arms[arm]['end'] for arm in arms)
        chromPerc = length / chromLen * 100
        if mySeg['arm'] in arms:           
            armLen = arms[mySeg['arm']]['length']
            armPerc = length / armLen * 100
        else:
            armPerc = 0

    logs = (seg['log2'] for seg in segs)
    pVals = (seg['pVal'] for seg in segs)
    cCovs = (seg['controlCov'] for seg in segs)
    tCovs = (seg['tumoralCov'] for seg in segs)
    logMean = statistics.mean(logs)
    pValMean = statistics.mean(pVals)
    cCovMean = statistics.mean(cCovs)
    tCovMean = statistics.mean(tCovs)

    mySeg['start'] = start
    mySeg['end'] = end
    mySeg['len'] = length
    mySeg['chromPerc'] = chromPerc
    mySeg['armPerc'] = armPerc
    mySeg['log2'] = logMean
    mySeg['pVal'] = pValMean
    mySeg['controlCov'] = cCovMean
    mySeg['tumotalCov'] = tCovMean

    return mySeg


def addArm(segment, armsDict):
    if not segment['chrom'] in armsDict:
        return 'ChromError'

    arms = armsDict[segment['chrom']]
    armSeg = ''
    for arm in arms:
        if utility.isOverlapping(segment['start'], segment['end'],arms[arm]['start'], arms[arm]['end']):
            armSeg = '%s,%s' %(armSeg, arms[arm]['name'])
    segment['arm'] = armSeg[1:]
    return segment

def addEventType(segment, maximum, minimum):
    segLog = segment['log2']
    if   segLog < minimum:
        evType = 'Del'
    elif segLog > maximum:
        evType = 'Amp'
    else:
        evType = 'Neu'
    segment['type'] = evType
    return segment
    

if __name__ == '__main__':
    main()
