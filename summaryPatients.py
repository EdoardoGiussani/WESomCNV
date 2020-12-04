#!/usr/bin/env python3

import utility
import argparse


def main():
    print('\nRunning annoteSegments.py')
    args = parseArgs()

    sTime = utility.startTime()

    segments = getSegments(args.inputFile)
    printOutput(segments['Amp'], args.outputBase, 'amp')
    printOutput(segments['Del'], args.outputBase, 'del')

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = '')

    parser.add_argument('inputFile', metavar = 'cumulativeFile',
            action='store', type=utility.existingFile,
            help='')
    parser.add_argument('-o', '--output', dest='outputBase',
            action='store', type=utility.existingFilePath, required=False,
            default=utility.workingDirectory() + '/output',
            help='Output file name')

    args = parser.parse_args()
    utility.printParameters(args)
    return args


def getSegments(inputFile):
    segments = {'Amp' : [], 'Del' : []}
    with open(inputFile, 'r') as inFile:
        header = utility.lineToHeader(inFile.readline())

        for line in inFile:
            segment = utility.lineToDict(line, header)
            segments[segment['type']].append(segment)

    return segments


def printOutput(segs, outbn, suf):
    outputFile = '%s.%s' % (outbn, suf)
    with open(outputFile, 'w') as outFile:
        outFile.write('patient\tgene\tlog2\n')
        for seg in segs:
            for gene in seg['genes']:
                outFile.write('%s\t%s\t%s\n' % (seg['patient'], gene, seg['log2']))


if __name__ == '__main__':
    main()
