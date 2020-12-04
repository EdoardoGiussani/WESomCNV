#!/usr/bin/env python3


import time
import queue
import utility
import argparse
import threading
import statistics
import subprocess

filteredSegs = []

def main():
    print('\nRunning coverageFilter.py')
    args = parseArgs()

    sTime = utility.startTime()

    segments = getSegments(args.inputFile)
    tList = []
    for segment in segments:
        t = threading.Thread(target = coverageMeans, args = (segment, args.controlFile, args.tumoralFile, args.bedFile, args.refFile, args.minCov))
        t.start()
        tList.append(t)

        while len(threading.enumerate()) > 5:
            time.sleep(1)

    for t in tList:
        t.join()
    utility.writeOutput(filteredSegs, args.outputFile)

    eTime = utility.endTime()
    utility.executionTime(sTime, eTime)


def parseArgs():
    parser = argparse.ArgumentParser(description = 'Filter out segments with a medium coverage less than a minum value')
    parser.add_argument('inputFile', metavar = 'annotedFile',
                        action='store', type=utility.existingFile,
                        help='Input file from annoteSegments.py')

    parser.add_argument('-c','--control', dest = 'controlFile',
                        action='store', type=utility.existingFile, required=True,
                        help='Control bam file')
    parser.add_argument('-t','--tumor', dest = 'tumoralFile',
                        action='store', type=utility.existingFile, required=True,
                        help='Tumoral bam file')
    parser.add_argument('-b', '--bed-file', dest='bedFile',
                        action='store', type=utility.existingFile, required=True,
                        help='Bed file')
    parser.add_argument('-r', '--reference', dest='refFile',
                        action='store', type=utility.existingFile, required=True,
                        help='Reference file')

    parser.add_argument('-o', '--output', dest='outputFile',
                        action='store', type=utility.existingFilePath, required=False, 
                        default=utility.workingDirectory() + '/output.coverage.tsv',
                        help='Output file name') 
    parser.add_argument('-m', '--min-coverage', dest='minCov',
                        action='store', type=int, required=False,
                        default=25,
                        help='Minimum coverage value for filter out segments')

    args = parser.parse_args()
    utility.printParameters(args)
    return args


def getSegments(segmentFile):
    segs = []
    with open(segmentFile, 'r') as inFile:
        header = utility.lineToHeader(inFile.readline())
        for line in inFile:
            segment = utility.lineToDict(line, header)
            segs.append(segment)
    return segs


def coverageMeans(segment, control, tumoral, bed, ref, threshold):
    region = str(segment['chrom']) + ':' + str(segment['start']) + '-' + str(segment['end'])
    cmdList = ['samtools', 'mpileup', '-q', '1', '-l', bed, '-r', region, '-f', ref, control, tumoral]
    #utility.printCmdLine('Samtools', cmdList)

    cCover = []
    tCover = []
    proc = subprocess.Popen(cmdList, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT)
    for line in iter(proc.stdout.readline, b''):
        line = line.decode('utf-8')
        fields = line.split()
        try:
            if fields[3].isnumeric() and fields[6].isnumeric():
                if int(fields[3]) > 0 or int(fields[6])> 0:
                    cCover.append(int(fields[3]))
                    tCover.append(int(fields[6]))
        except:
            continue

    segment['controlCov'] = 0
    segment['tumoralCov'] = 0
    if cCover and tCover:
        segment['controlCov'] = statistics.mean(cCover)
        segment['tumoralCov'] = statistics.mean(tCover)
    if segment['controlCov'] >= threshold and segment['tumoralCov'] >= threshold:
        filteredSegs.append(segment)


if __name__ == '__main__':
    main() 
