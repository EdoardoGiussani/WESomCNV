#!/usr/bin/env python3

import utility
import argparse


def main():
    print('\nRunning cancerFilter.py')
    
    args = parseArgs()

    sTime = utility.startTime()

    geneList =  getGenes(args.geneFile)
    filteredSegs = filterSegmentGenes(args.inputFile, geneList)
    utility.writeOutput(filteredSegs, args.outputFile)

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = 'Filter the annoteSegments.py or coverageFilter.py output with a given list of genes of interest') 
    parser.add_argument('inputFile', metavar='inputFile',
                        action='store', type=utility.existingFile, 
                        help='annoteSegments.py or coverageFilter.py output file')
    parser.add_argument('-o', '--output', dest='outputFile',
                        action='store', type=utility.existingFilePath, required=False,
                        default=utility.workingDirectory() + '/output.cancer.tsv',  
                        help='Output file name') 
    parser.add_argument('-r', '--gene-file', dest='geneFile',
                        action='store', type=utility.existingFile, required=False,
                        default=utility.programDirectory() + '/refs/cancerGenes.tsv',
                        help='A reference file with a list of genes of interest')
    args = parser.parse_args()
    utility.printParameters(args)
    return args


def getGenes(genesFile):
    headerList = ['name']
    genesList = []
    with open(genesFile, 'r') as genFile:
        header = utility.lineToHeader(genFile.readline(), headerList)
        for line in genFile:
            gene = utility.lineToDict(line, header)
            genesList.append(gene['name'])
    return genesList


def filterSegmentGenes(segmentsFile, geneList):
    segments = []
    with open(segmentsFile, 'r') as inFile:
        header = utility.lineToHeader(inFile.readline())
        for line in inFile:
            filteredGenes = []
            segment = utility.lineToDict(line, header)
            for gene in segment['genes']:
                if gene in geneList:
                    filteredGenes.append(gene)
            if filteredGenes:
                segment['genes'] = filteredGenes
                segments.append(segment)
    return segments


if __name__ == '__main__':
    main() 
