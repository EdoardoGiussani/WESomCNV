import os
import sys
import glob
import inspect
import datetime

#PRINT TIMER
def startTime():
    sTime = datetime.datetime.now()
    print('\nRun started at %s' %(sTime.strftime('%H:%M:%S %d/%m/%Y')))
    return sTime
def endTime():
    eTime = datetime.datetime.now()
    print('\nRun endeded at %s' %(eTime.strftime('%H:%M:%S %d/%m/%Y')))
    return eTime
def executionTime(startTime, endTime):
    exeTime = endTime - startTime
    print('Execution time: %s' % (str(exeTime)))
    return exeTime


#PRINT INFORMATIONS
def printParameters(parameters):
    print('Paramenters:')
    for par in vars(parameters):
        print('\t%s: %s' %(par, str(getattr(parameters, par))))
    return 

def printCmdLine(cmdName, cmdList):
    cmdLine = ''
    for cmd in cmdList:
        cmdLine = '%s%s ' %(cmdLine, cmd) 
    print('\n%s: %s' %(cmdName, cmdLine))
    return cmdLine

#PATH CHECK
def checkFile(filePath):
    filePath = os.path.abspath(filePath)
    if os.path.isfile(filePath):
        return True
    else:
        return False
def existingFile(filePath):
    if checkFile(filePath):
        return filePath
    else:
        sys.exit('File %s not found, execution stopped' %(filePath))

def checkDirectory(directoryPath):
    directoryPath = os.path.abspath(directoryPath)
    if os.path.isdir(directoryPath):
        return True
    else:
        return False
def existingDirectory(directoryPath):
    if checkDirectory(directoryPath):
        return directoryPath
    else:
        sys.exit('Directory %s not found, execution stopped' %(directoryPath))

def checkFilePath(filePath):
    directoryPath = os.path.dirname(filePath)
    return checkDirectory(directoryPath)
def existingFilePath(filePath):
    directoryPath = os.path.dirname(filePath)
    existingDirectory(directoryPath)
    return filePath

def getFiles(path):
    files = glob.glob(path)
    return files

#CREATE PATH
def createDirectory(dirPath, newDir):
    newPath = '%s/%s' %(dirPath, newDir)
    if not checkDirectory(newPath):
        try:
            os.mkdir(newPath)
            print('Created folder %s' %(newPath))
        except OSError:
            sys.exit('Failed to create folder %s' %(newPath))
    else:
        print('This folder already exist: %s' %(newPath))
    return newPath

#GET PATHS
def programDirectory():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
def workingDirectory():
    return os.getcwd()
def getProgramPath(program):
    programPath = '%s/%s' % (programDirectory(), program)
    existingFile(programPath)
    return programPath


#WORK WITH SEGMENTS
segList = ('patient', 'chrom', 'start', 'end', 'len', 'arm', 'type', 'controlCov', 'tumoralCov', 'log2', 'pVal', 'armPerc', 'chromPerc', 'frequency', 'genes')
segInts = ('start', 'end', 'len')
segFloats = {'controlCov' : 2, 
                'tumoralCov' : 2, 
                'log2' : 4, 
                'pVal' : 1000, 
                'armPerc' : 4, 
                'chromPerc' : 4,
                'frequency' : 2}
segLists = ['genes']

def lineToHeader(headLine, headsList = segList):
    headDict = {}
    headLine = headLine.rstrip('\n')
    heads = headLine.split('\t')

    for head in heads:
        if not head in headsList:
            print('Header contains unrecognized %s' %(head))
        headDict[head] = heads.index(head)
    return headDict

def lineToDict(line, header, ints = segInts, floats = segFloats, lists = segLists):
    myDict = {}
    line = line.strip('\n')
    fields = line.split('\t')

    for param in header:
        value = fields[header[param]]
        if param in ints:
            value = int(value)
        elif param in floats:
            value = float(value)
        elif param in lists:
            value = value.split(',')
        myDict[param] = value
    return myDict


def headerToLine(header, headsList = segList):
    headLine = ''
    for param in headsList:
        if param in header:
            headLine = '%s\t%s' %(headLine, param)
    return headLine[1:]

def dictToLine(myDict, headsList = segList, floats = segFloats, lists = segLists):
    line = ''
    for param in headsList:
        if param in myDict:
            if param in floats:
                myDict[param] = round(myDict[param], floats[param])
            if param in lists:
                myDict[param] = listToLine(myDict[param], ',')
            line = '%s\t%s' %(line, str(myDict[param]))
    return line[1:]

def listToLine(myList, separator):
    line = ''
    for e in myList:
        line = '%s%s%s' % (line, separator, e)
    return line [1:]


def writeOutput(elements, outputFile):
    lines = []
    for element in elements:
        lines.append([element['patient'], element['chrom'], element['start'], dictToLine(element)])
    lines.sort(key=lambda x: (x[0], x[1], x[2]))

    with open(outputFile, 'w') as outFile:
        outFile.write(headerToLine(elements[0]) + '\n' )
        for line in lines: 
            outFile.write(line[3] + '\n')


def isOverlapping(start1, end1, start2, end2):
    if start1 <= end2 and start2 <= end1:
        return True
    return False





























