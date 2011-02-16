#!/usr/bin/python

import sys
import os
import shutil
import signal
import pickle
import re
import subprocess
import logging
import ConfigParser

_ExecPath = os.path.abspath(os.path.dirname(__file__)) + "/"

#_LogFilePath = _ExecPath + 'sync.log'
#logging.basicConfig(filename=_LogFilePath,level=logging.DEBUG)

def main():

    if len(sys.argv) == 1:
        print 'usage: sync.py push|pull'
        exit()
        
    configFilePath = _ExecPath + 'sync.conf'
    
    hostAndPath, exclude = getConfig(configFilePath)
    
    userCommand = sys.argv[1].lower()
    
    if userCommand == 'push':
        rsyncProcess = runProcess(getRsyncCommand(_ExecPath, hostAndPath, exclude, True))
        rsyncProcess.wait()
        if confirm("You will replace all remote host data with your data. Are you absolutely sure you want to do this?"):
            rsyncProcess = runProcess(getRsyncCommand(_ExecPath, hostAndPath, exclude, False))
            rsyncProcess.wait()
    elif userCommand == 'pull':
        rsyncProcess = runProcess(getRsyncCommand(hostAndPath+'/', _ExecPath, exclude, True))
        rsyncProcess.wait()
        if confirm("You will replace all your data with the remote host data. Are you absolutely sure you want to do this?"):
            rsyncProcess = runProcess(getRsyncCommand(hostAndPath+'/', _ExecPath, exclude, False))
            rsyncProcess.wait()
    

def getRsyncCommand(source, dest, exclude, dryRun):
    
    rsyncCommand = ['rsync', '--verbose', '--progress', '--stats', '--compress', '--recursive', '--backup', '--backup-dir=rsyncBackup~', '--exclude', 'rsyncBackup~', '--links', '--delete', '--times']
    
    if dryRun:
        rsyncCommand.append('--dry-run')
    
    for folder in exclude:
        rsyncCommand.append('--exclude')
        rsyncCommand.append(folder) 
    
    rsyncCommand.append(source)
    rsyncCommand.append(dest)

    return(rsyncCommand)
    
def getConfig(configFilePath):
    
    execConfig = ConfigParser.RawConfigParser() 
    execConfig.read(configFilePath)
    
    exclude = []
    
    try:
        remoteHost = execConfig.get('sync', 'remoteHost')
        hostTreePath = execConfig.get('sync', 'hostTreePath')
        if execConfig.has_option('sync', 'exclude'):
            excludeString = execConfig.get('sync', 'exclude')
            exclude = splitStripString(excludeString, ",")
    
    except ConfigParser.NoSectionError as e:
        print('There was a problem with your config file. Please make sure it exists. Attempted path: ' + configFilePath + ' Error: ' + str(e))
        exit()
    except ConfigParser.NoOptionError as e:
        print('There was a problem with your config file. You were missing at least one option we require. Error: ' + str(e))
        exit()
        
    return(remoteHost + ":" + hostTreePath, exclude)


def splitStripString(str, delim):

    strSplit = str.split(delim)

    def strip(x): return x.strip()

    strSplit = map(strip, strSplit)

    return strSplit
    
def runProcess(psData, filePathToPipe = ''):

    try:
        if filePathToPipe != '':
            fileToPipe = open(filePathToPipe, 'w')
            ps = subprocess.Popen(psData, shell=False, stdout=fileToPipe, stderr=fileToPipe)
        else:
            ps = subprocess.Popen(psData, shell=False)
        
        return(ps)

    except OSError as e:
        print("There was a problem starting the rsync process. Error: " + e.msg)        
        exit()


def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s (%s/%s): ' % (prompt, 'Y', 'n')
    else:
        prompt = '%s (%s/%s): ' % (prompt, 'N', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


main()



