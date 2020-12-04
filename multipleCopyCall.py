#!/usr/bin/env python3

import time
import utility
import argparse
import threading
import subprocess

def main():
    print('\nRunning multipleCopyCall.py')

    args = parseArgs()
    
    sTime = utility.startTime()

    tList = []
    tmpDir = utility.createDirectory(args.outputFolder, 'copyCalls')

    for i in range(args.iteration):
        ccDir = utility.createDirectory(tmpDir, str(i))
        t = threading.Thread(target = runCopyCall, args = (args.inputFile, ccDir, ))
        t.start()
        tList.append(t)

        while len(threading.enumerate()) > 5:
            time.sleep(1)

    for t in tList:
        t.join()


    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)
    return


def parseArgs():
    parser = argparse.ArgumentParser(description = '')

    parser.add_argument('inputFile', metavar='copynumberFile',
                        action='store', type=utility.existingFile,
                        help='')
    parser.add_argument('iteration', metavar='iteration',
                        action='store', type=int,
                        help='')
    parser.add_argument('-o', '--output', dest='outputFolder',
                        action='store', type=utility.existingDirectory, required=False,
                        default=utility.workingDirectory(),
                        help='Output folder')
   
    args = parser.parse_args()
    utility.printParameters(args)
    return args


def runCopyCall(inFile, outDir):
    prog = utility.getProgramPath('copyCaller.py')

    cmdList = [prog, '-o', outDir, inFile] 
    utility.printCmdLine('copyCaller', cmdList)

    subprocess.call(cmdList)
    #runProg = subprocess.Popen(cmdList)
    #runProg.wait()

    return outDir + '/output.r.tsv'


def runMergeSegments(inFile, armRef, tMin, tMax, patientId, outDir):
    prog   = utility.getProgramPath('mergeSegments.py')
    valOut = outDir + '/output.merged.tsv'

    cmdList = [prog, '-o', valOut, '-n', patientId]
    if not armRef == None:
        cmdList.append('-r')
        cmdList.append(armRef)
    if not tMin == None:
        cmdList.append('-d')
        cmdList.append(str(tMin))
    if not tMax == None:
        cmdList.append('-a')
        cmdList.append(str(tMax))
    cmdList.append(inFile)
    utility.printCmdLine('mergeSegment', cmdList)

    subprocess.call(cmdList)
    #runProg = subprocess.Popen(cmdList)
    #runProg.wait()

    return valOut


def runAnnoteSegments(inFile, annRef, outDir):
    prog = utility.getProgramPath('annoteSegments.py')
    valOut = outDir + '/output.annotated.tsv'

    cmdList = [prog, '-o', valOut]
    if not annRef == None:
        cmdList.append('-r')
        cmdList.append(annRef)
    cmdList.append(inFile)
    utility.printCmdLine('annoteSegment', cmdList)

    subprocess.call(cmdList)
    #runProg = subprocess.Popen(cmdList)
    #runProg.wait()

    return valOut


if __name__ == '__main__':
    main()
