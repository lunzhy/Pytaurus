__author__ = 'lunzhy'
import os, sys
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)
from pytaurus import *

def prepareProject(prj_path):
    print('nothing to do with prepare project.')
    return


def cleanProject(prj_path):
    #clean the directory recursively
    delFiles(prj_path)
    return


def delFiles(path):
    for file in os.listdir(path):
        if file in Files_Remain:
            continue
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            delFiles(file_path)
    return