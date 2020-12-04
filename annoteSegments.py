#!/usr/bin/env python3

import utility
import argparse


def main():
    print('\nRunning annoteSegments.py')
    args = parseArgs()

    sTime = utility.startTime()

    genesDict = getAnnotationInfo(args.annotationFile)
    segments = annoteSegments(args.inputFile, genesDict)
    utility.writeOutput(segments, args.outputFile)
    
    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = 'Annote segments from mergeSegments.py using a reference file. It discard "Neutral" segments and segments that don\'t intersect any exon')

    parser.add_argument('inputFile', metavar = 'mergedFile',
                        action='store', type=utility.existingFile,
                        help='Input file from mergeSegments.py')

    parser.add_argument('-o', '--output', dest='outputFile',
                        action='store', type=utility.existingFilePath, required=False, 
                        default=utility.workingDirectory() + '/output.annotated.tsv',
                        help='Output file name') 
    parser.add_argument('-r', '--ref-annotation', dest='annotationFile',
                        action='store', type=utility.existingFile, required=False,
                        default=utility.programDirectory() + '/refs/genesReference.tsv',
                        help='Reference file for annotation')
    args = parser.parse_args()
    utility.printParameters(args)
    return args


def getAnnotationInfo(annoteFile):
    headsList = ['name2', 'chrom', 'start', 'end', 'exonCount', 'exonStarts', 'exonEnds']
    annInts = ['exonCount', 'start', 'end']
    genes = {}

    with open(annoteFile, 'r') as annFile:
        header = utility.lineToHeader(annFile.readline(), headsList)

        for line in annFile:        
            gene = utility.lineToDict(line, header, annInts)
            gene['chrom'] = gene['chrom'][3:]
            gene['exonStarts'] = gene['exonStarts'].split(',')[:-1]
            gene['exonStarts'] = list(map(int, gene['exonStarts']))
            gene['exonEnds'] = gene['exonEnds'].split(',')[:-1]
            gene['exonEnds'] = list(map(int, gene['exonEnds']))

            if not gene['chrom'] in genes:
                genes[gene['chrom']] = []
            genes[gene['chrom']].append(gene)
    return genes


def annoteSegments(segmentFile, annoteDict):
    segments = []
    with open(segmentFile, 'r') as inFile:
        header = utility.lineToHeader(inFile.readline())

        for line in inFile:
            segment = utility.lineToDict(line, header)
            segment['genes'] = []

            if segment['type'] == 'Neu':
                continue

            chromGenes = annoteDict[segment['chrom']]
            for gene in chromGenes:
                segment = geneOverlap(segment, gene)
            if segment['genes']:
                segments.append(segment)
    return segments


def geneOverlap(segment, gene):
    if utility.isOverlapping(segment['start'], segment['end'], gene['start'], gene['end']):
        if not gene['name2'] in segment['genes']:
            for i in range(gene['exonCount']):
                if utility.isOverlapping(segment['start'], segment['end'], gene['exonStarts'][i], gene['exonEnds'][i]):
                    segment['genes'].append(gene['name2'])
                    break
    return segment


if __name__ == '__main__':
    main() 
