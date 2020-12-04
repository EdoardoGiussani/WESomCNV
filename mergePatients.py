#!/usr/bin/env python3

import os
import sys
import utility
import argparse


def main():
    print('\nRunning mergePatients.py')
    args = parseArgs()
    if not args.inputFiles:
        sys.exit('No files found in path')
    sTime = utility.startTime()

    createCumulative(args.inputFiles, args.outputFile)

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = '')

    parser.add_argument('inputFiles', metavar = 'filesList',
            action='store', nargs='+', type=utility.existingFile, 
            help='Input file from mergeSegments.py')

    parser.add_argument('-o', '--output', dest='outputFile',
            action='store', type=utility.existingFilePath, required=False,
            default=utility.workingDirectory() + '/output.cumulative.tsv',
            help='Output file name')

    args = parser.parse_args()
    utility.printParameters(args)
    return args


def createCumulative(inputFiles, outputFile):
    with open(outputFile, 'w') as outFile:
        with open (inputFiles[0]) as inHeader:
            outFile.write(inHeader.readline())

        for inputFile in inputFiles:
            with open(inputFile, 'r') as inFile:
                inFile.readline()
                for line in inFile:
                    outFile.write(line)


if __name__ == '__main__':
    main()
