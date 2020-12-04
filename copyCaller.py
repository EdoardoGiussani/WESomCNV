#!/usr/bin/env python3

import utility
import argparse
import subprocess

def main():
    print('\nRunning copyCaller.py')

    args = parseArgs() 
    varFile = utility.getProgramPath('varScan.jar')
    rScript = utility.getProgramPath('segmentation.R')
    cnFile = '%s/output.cn.call' %(args.outputFolder)

    sTime = utility.startTime()

    adjustment = 0
    correction = 0
    counter = -1

    while not adjustment == 'Centered':
        counter = counter + 1
        correction = correction + adjustment

        copyCall(varFile, 
                 args.inputFile,
                 cnFile,
                 correction)
        removeCommas(cnFile)
        adjustment = runRScript(rScript,
                                cnFile,
                                args.outputFolder)
        
    print('\nFinal correction value is %s' %(str(correction)))
    print('Number of adjustments: %s' %(str(counter)))

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)
    return


def parseArgs():
    parser = argparse.ArgumentParser(description = 'Merge segments from R output')

    parser.add_argument('inputFile', metavar='copynumberFile',
                        action='store', type=utility.existingFile,
                        help='Input file from varScan copynumber')

    parser.add_argument('-o', '--output', dest='outputFolder',
                        action='store', type=utility.existingDirectory, required=False,
                        default=utility.workingDirectory(),
                        help='Output folder')

    args = parser.parse_args()
    utility.printParameters(args)
    return args


def copyCall(varScan, inFile, outFile, correction):
    valHom = outFile + '.homdel'
    cmdCn = ['java', '-jar', varScan, 'copyCaller', inFile, '--output-file', outFile, '--output-homdel-file', valHom]
    if not correction == 0:
        if correction > 0:
            optMv = '--recenter-up'
        else:
            optMv = '--recenter-down'
        cmdCn.append(optMv)
        cmdCn.append(str(abs(correction)))
    utility.printCmdLine('Varscan', cmdCn)

    runCn = subprocess.Popen(cmdCn,
                              stderr=subprocess.PIPE)
    runCn.wait()
    return


def removeCommas(inFile):
    cmdSed = ['sed', '-i', 's/\,/\./g', inFile]
    utility.printCmdLine('Sed', cmdSed)

    subprocess.call(cmdSed)
    return


def runRScript(rScript, inFile, outDir):
    prog = rScript
    args = [inFile, outDir]

    cmdR = [prog] + args
    utility.printCmdLine('R', cmdR)

    adjustment = subprocess.check_output(cmdR, 
                                         universal_newlines=True,
                                         stderr=subprocess.PIPE)
    if adjustment == 'Centered':
        print('\nCalls centered')
        return adjustment   
    else:
        print('\nAdjustment value is %s' %(adjustment))
        return float(adjustment)



if __name__ == '__main__':
    main()
