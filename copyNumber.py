#!/usr/bin/env python3

import os 
import utility
import argparse
import subprocess

def main():
    print('\nRunning copyNumber.py')

    args = parseArgs()
    varFile = utility.getProgramPath('varScan.jar')

    sTime = utility.startTime()

    os.chdir(args.outputFolder)
    pileUpBams(varFile,
               args.controlFile, 
               args.tumoralFile, 
               args.bedFile, 
               args.refFile,
               args.outputFolder) 

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)
    return


def parseArgs():            #TODO: improve descriptions
    parser = argparse.ArgumentParser(description = 'Use Samtools and VarScan to create an output file for copy number variation study')        

    parser.add_argument('controlFile', metavar='controlBam',
                        action='store', type=utility.existingFile,
                        help='Bam file for control samples, with index')
    parser.add_argument('tumoralFile', metavar='tumoralBam',
                        action='store', type=utility.existingFile,
                        help='Bam file for tumoral samples, with index')

    parser.add_argument('-r', '--reference', dest='refFile',
                        action='store', type=utility.existingFile, required=True,
                        help='Indexed reference file')

    parser.add_argument('-o', '--output', dest='outputFolder',
                        action='store', type=utility.existingDirectory, required=False,
                        default=utility.workingDirectory(),
                        help='Output folder')
    parser.add_argument('-b', '--bed', dest='bedFile',
                        action='store', type=utility.existingFile, required=False,
                        help='Bed file')

    args = parser.parse_args()
    utility.printParameters(args)
    return args


def pileUpBams(varScan, control, tumoral, bed, ref, outFolder):
    cmdSam = ['samtools', 'mpileup', '-q', '1', '-f', ref, control, tumoral]
    if not bed is None:
        cmdSam.insert(4, '-l')
        cmdSam.insert(5, bed)
    utility.printCmdLine('Samtools pileup', cmdSam)

    cmdVSc = ['java', '-jar', varScan, 'copynumber', 'default', '--mpileup', '1']
    utility.printCmdLine('Varscan', cmdVSc)
    
    runSam = subprocess.Popen(cmdSam,
                              stdout=subprocess.PIPE)
    runVSc = subprocess.Popen(cmdVSc,
                              stdin=runSam.stdout)
    runSam.wait()
    runVSc.wait()
    return


if __name__ == '__main__':
    main()
