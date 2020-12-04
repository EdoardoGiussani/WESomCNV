#!/usr/bin/env python3 

import sys
import utility
import argparse
import subprocess
import configparser


def main():
    print('\nRunning runCNVAnalysis.py\n')

    configFile = parseArgs()
    config = getArgsFromFIle(configFile.configFile)
    
    sTime = utility.startTime()

    copyNumFile = runCopyNumber(config['Input']['controlBam'],
                                config['Input']['tumoralBam'],
                                config['References']['bedFile'],
                                config['References']['refFile'],
                                config['Output']['outputFolder'],
                                config['Analysis'].getboolean('copyNumber'))

    multipleCCDir = runMultipleCopyCall(copyNumFile,
                                        config['Parameters']['iterations'],
                                        config['Output']['outputFolder'],
                                        config['Analysis'].getboolean('copyCalls'))

    cumulativeCC = runMergeCopyCalls(multipleCCDir,
                                     'output.r.tsv',
                                     config['Parameters']['genePercentage'],
                                     config['Input']['patient'],
                                     config['Output']['outputFolder'],
                                     config['Analysis'].getboolean('mergeCopyCalls'))

    coverageFile = runCoverageFilter(cumulativeCC,
                                     config['Input']['controlbam'],
                                     config['Input']['tumoralbam'],
                                     config['References']['bedfile'],
                                     config['References']['reffile'],
                                     config['Parameters']['minCoverage'],
                                     config['Output']['outputfolder'],
                                     config['Analysis'].getboolean('coverageFilter'))

    mergedFile = runMergeSegments(coverageFile,
                                  config['References']['armreffile'],
                                  config['Parameters']['upperlimit'],
                                  config['Parameters']['lowerlimit'],
                                  config['Output']['outputfolder'],
                                  config['Analysis'].getboolean('mergeSegments'))

    annotedFile = runAnnoteSegments(mergedFile,
                                    config['References']['annotationfile'],
                                    config['Output']['outputfolder'],
                                    config['Analysis'].getboolean('annoteSegments'))

    cancerFile = runGeneFilter(annotedFile,
                               config['References']['cancerGenesReference'],
                               config['Output']['outputfolder'],
                               config['Analysis'].getboolean('geneFilter'))

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = '')      #Add program description
    
    parser.add_argument('configFile', metavar = 'configuation-file',
            action='store', type=utility.existingFile,
            help='')                                        #Add argument description
    args = parser.parse_args()
    utility.printParameters(args)
    return args


def getArgsFromFIle(cFile):
    config = configparser.ConfigParser()
    config.read(cFile)

    for section in config.sections():
        print('\n' + section)
        for arg in config[section]:
            if section == 'Analysis':
                par = str(config[section].getboolean(arg))
            else:
                par = config[section][arg]
            print('\t%s: %s' %(arg, par))
    return config


def runCmd(name, cmdList, toRun):
    utility.printCmdLine(name, cmdList)

    if toRun:
        result = subprocess.call(cmdList)
        if not result == 0:
            sys.exit('%s ended with errors' % (name))


def runCopyNumber(control, tumoral, bed, ref, outFolder, toRun):
    prog = utility.getProgramPath('copyNumber.py')

    cmdList = [prog, '-b', bed, '-r', ref, '-o', outFolder, control, tumoral]
    runCmd('CopyNumber', cmdList, toRun)

    return outFolder + '/output.copynumber'


def runMultipleCopyCall(copyFile, iterations, outFolder, toRun):
    prog = utility.getProgramPath('multipleCopyCall.py')

    cmdList = [prog, '-o', outFolder, copyFile, iterations]
    runCmd('MultipleCopyCall', cmdList, toRun)

    return outFolder  + '/copyCalls'


def runMergeCopyCalls(ccDir, fileName, threshold, patient, outFolder, toRun):
    prog = utility.getProgramPath('mergeCopyCalls.py')
    filesPath = '%s/*/%s' % (ccDir, fileName)
    outFile = outFolder + '/output.cumulative.tsv'

    cmdList = [prog, '-o', outFile, '-n', patient, filesPath, threshold]
    runCmd('MergeCopyCalls', cmdList, toRun)

    return outFile 
    

def runCoverageFilter(inFile, control, tumoral, bed, ref, minCov, outFolder, toRun):
    prog = utility.getProgramPath('filterCoverage.py')
    outFile = outFolder + '/output.coverage.tsv'

    cmdList = [prog, '-c', control, '-t', tumoral, '-b', bed, '-r', ref, '-m', minCov, '-o', outFile, inFile]
    runCmd('CoverageFilter', cmdList, toRun)

    return outFile


def runMergeSegments(inFile, armRef, maxThreshold, minThreshold, outFolder, toRun):
    prog = utility.getProgramPath('mergeSegments.py')
    outFile = outFolder + '/output.merged.tsv'

    cmdList = [prog, '-r', armRef, '-a', maxThreshold, '-d', minThreshold, '-o', outFile, inFile]
    runCmd('MergeSegments', cmdList, toRun)

    return outFile

def runAnnoteSegments(inFile, annRef, outFolder, toRun):
    prog = utility.getProgramPath('annoteSegments.py')
    outFile = outFolder + '/output.annotated.tsv'

    cmdList = [prog, '-r', annRef, '-o', outFile, inFile]
    runCmd('AnnoteSegments', cmdList, toRun)

    return outFile 


def runGeneFilter(inFile, ref, outFolder, toRun):
    prog = utility.getProgramPath('filterGenes.py')
    outFile = outFolder + '/output.cancer.tsv'

    cmdList = [prog, '-r', ref, '-o', outFile, inFile]
    runCmd('GeneFilter', cmdList, toRun)

    return outFile


if __name__ == '__main__':
    main()
