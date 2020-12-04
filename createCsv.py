#!/usr/bin/env python3

import utility
import argparse


def main():
    print('\nRunning createCsv.py')

    args = parseArgs()
    sTime = utility.startTime()

    genes, variationTypes, patients = getGenes(args.inputFiles)
    lines = createCsv (genes, variationTypes, patients)
    line1, line2 = csvHeader(patients, variationTypes)
    lines.insert(0, line2)
    lines.insert(0, line1)
    writeCsv(lines, args.outputFile)

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = '')

    parser.add_argument('inputFiles', metavar = 'filesList',
            action='store', nargs='*', type=utility.existingFile,
            help='Input file from mergeSegments.py')

    parser.add_argument('-o', '--output', dest='outputFile',
            action='store', type=utility.existingFilePath, required=False,
            default=utility.workingDirectory() + '/output.cumulative.csv',
            help='Output file name')

    args = parser.parse_args()
    utility.printParameters(args)
    return args


def getGenes(inputFiles):
    genes = {}
    variationTypes = []
    patients = []
    headsList = ['patient','gene','log2']
    for geneFile in inputFiles:
        with open(geneFile, 'r') as inFile:
            variationType = geneFile.split('.')[-1]
            variationTypes.append(variationType)
            header = utility.lineToHeader(inFile.readline(), headsList)

            for line in inFile:
                patGen = utility.lineToDict(line, header)
                gene = patGen['gene']
                patient = patGen['patient']
                log2 = patGen['log2']

                if not gene in genes:
                    genes[gene] = {}

                if not variationType in genes[gene]:
                    genes[gene][variationType] = {}

                if not patient in genes[gene][variationType]:
                    genes[gene][variationType][patient] = log2
                    if not patient in patients:
                        patients.append(patient)
                else:
                    genes[gene][variationType][patient] = max(genes[gene][variationType][patient], log2)


    return genes, variationTypes, patients


def createCsv(genes, varList, patients):
    lines = []
    patients.sort()

    for gene in genes:
        line = '%s,' % (gene)
        for patient in patients:
            for variation in varList:
                if not variation in genes[gene]:
                    genes[gene][variation] = []
                if patient in genes[gene][variation]:
                    line = '%s%s' % (line, genes[gene][variation][patient])
                line = '%s%s' % (line, ',')
        lines.append(line)
    return lines


def csvHeader(patients, varList):
    lineP = ','
    lineV = ','
    for patient in patients:
        lineP = '%s%s' % (lineP, patient)
        for var in varList:
            lineP = '%s%s' %(lineP, ',')
            lineV = '%s%s%s' % (lineV, var, ',')
    return lineP, lineV


def writeCsv(lines, outputFile):
    with open(outputFile, 'w') as outFile:
        for line in lines:
            outFile.write('%s\n' %(line))


if __name__ == '__main__':
    main()
