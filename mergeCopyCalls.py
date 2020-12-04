#!/usr/bin/env python3

import os
import utility
import argparse
import statistics
import filterGenes


def main():
    print('\nRunning mergeCopyCalls.py\n')

    args = parseArgs()
    sTime = utility.startTime()

    segmentsDict = segmentsCollector(args.inputFiles, args.patientId)
    total = len(args.inputFiles)
    segments = filterDict(segmentsDict, args.threshold, total)
    utility.writeOutput(segments, args.outputFile)

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = '')


    parser.add_argument('inputFiles', metavar='copyCalls',
                        action='store', type=utility.getFiles,
                        help='')
    parser.add_argument('threshold', metavar='threshold',
                        action='store', type=int,
                        help='')
    parser.add_argument('-n', '--patient-id', dest='patientId',
                        action='store', type=str, required=True,
                        help='')
    parser.add_argument('-o', '--output', dest='outputFile',
            action='store', type=utility.existingFilePath, required=False,
            default=utility.workingDirectory() + '/output.cumulative.tsv',
            help='')

    args = parser.parse_args()
    utility.printParameters(args)
    return args


def segmentsCollector(myFiles, patientId):
    segments = {}
    for inFile in myFiles:
        segments = getSegmentsFromFile(inFile, segments, patientId)
    return segments


def getSegmentsFromFile(inputFile, segs, patientId):
    with open(inputFile, 'r') as inFile:
        header = utility.lineToHeader(inFile.readline())
        for line in inFile:
            segment = utility.lineToDict(line, header)
            segment['patient'] = patientId
            if segment['start'] in segs:
                if segment['end'] in segs[segment['start']]:
                    segs[segment['start']][segment['end']]['log2'].append(segment['log2'])
                    segs[segment['start']][segment['end']]['pVal'].append(segment['pVal'])
                else:
                    segment['log2'] = [segment['log2']]
                    segment['pVal'] = [segment['pVal']]
                    segs[segment['start']][segment['end']] = segment
            else:
                segment['log2'] = [segment['log2']]
                segment['pVal'] = [segment['pVal']]
                segs[segment['start']] = {segment['end'] : segment}
    return segs


def filterDict(segDict, threshold, total):
    segs = []
    minCounter = threshold * total / 100

    for start in segDict:
        startDict = segDict[start]
        ends = []
        for end in startDict:
            ends.append(startDict[end]['end'])
        ends.sort(reverse = True)

        startCounter = 0
        for end in ends:
            endCounter = len(startDict[end]['log2'])
            startCounter = startCounter + endCounter
            if startCounter >= minCounter:
                startDict[end]['log2'] = statistics.mean(startDict[end]['log2'])
                startDict[end]['pVal'] = statistics.mean(startDict[end]['pVal'])
                startDict[end]['frequency'] = startCounter / total * 100
                segs.append(startDict[end])
                break
    return segs


if __name__ == '__main__':
    main()
