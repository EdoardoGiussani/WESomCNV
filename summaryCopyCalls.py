#!/usr/bin/env python3

import os
import utility
import operator
import argparse


def main():
    print('\nRunning summaryCopyCalls.py\n')

    args = parseArgs()

    sTime = utility.startTime()

    genesDict, iterations = iterateFiles(args.inputDir)
    genesList = geneStatistic(genesDict, iterations)
    printOutput(genesList, args.outputFile)

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = '')

    parser.add_argument('inputDir', metavar='copyCallsDir',
                        action='store', type=utility.existingDirectory,
                        help='')

    parser.add_argument('-o', '--output', dest='outputFile',
                        action='store', type=utility.existingFilePath, required=False,
                        default=utility.workingDirectory() + '/copyCalls.summary.tsv',
                        help='')

    args = parser.parse_args()
    utility.printParameters(args)
    return args


def iterateFiles(inputDir):
    counter = 0
    genesDict = {}
    subDirs = os.listdir(inputDir)
    for subDir in subDirs:
        subDir = '%s/%s' %(inputDir, subDir)
        if os.path.isdir(subDir):
            inFile = '%s/%s' %(subDir, 'output.annotated.tsv') 
            if os.path.isfile(inFile):
                counter = counter + 1
                fileGenes = genesFromFile(inFile)
                genesDict = updateGenesDict(genesDict, fileGenes)
    
    return genesDict, counter


def genesFromFile(inputFile):
    geneList = []

    with open(inputFile, 'r') as inFile:
        header = utility.lineToHeader(inFile.readline())
        for line in inFile:
            segment = utility.lineToDict(line, header)
            for gene in segment['genes']:
                if not gene in geneList:
                    geneList.append(gene)
    
    return geneList

def updateGenesDict(myDict, myGenes):
    for gene in myGenes:
        if not gene in myDict:
            myDict[gene] = 1
        else:
            myDict[gene] = myDict[gene] + 1
    return myDict


def geneStatistic(myDict, iterations):
    genesList = []
    for gene in myDict:
        geneCount = myDict[gene]
        genePerc = geneCount / iterations * 100
        genesList.append([gene, geneCount, genePerc])
    genesList.sort(key=lambda x: x[1], reverse=True)
    return genesList

def printOutput(genesList, outputFile):
    with open(outputFile, 'w') as outFile:
        for gene in genesList:
            line = '%s\t%s\t%s' %(gene[0], gene[1], str('%.2f' %(gene[2])))
            outFile.write(line + '\n')


if __name__ == '__main__':
    main()
