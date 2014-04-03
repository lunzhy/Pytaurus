__author__ = 'lunzhy'
import os, sys, math, re
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)
from pytaurus import *
from operator import itemgetter


def prepareProject(prj_path):
    if os.path.exists(prj_path):
        cleanProject(prj_path)
    # print('nothing to do with prepare project.')
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


def isMajorTime(time):
    return math.log10(time) == math.floor(math.log10(time))


def parseSimTime(file_path):
    with open(file_path, 'r') as f:
        info_line = f.readline()
        patt = re.compile(r'(?<=\[).*?(?=\])')
        match = re.search(patt, info_line)
        if match is None:
            print('cannot parse time')
        else:
            time = float(match.group())
    return time


def searchFilePathByTime(folder, pattern, time):
    time_filepath = []  # stores tuple (time, file_path)
    for file in os.listdir(folder):
        if pattern in file:
            file_path = os.path.join(folder, file)
            time_filepath.append((parseSimTime(file_path), file_path))
    time_filepath = sorted(time_filepath, key=itemgetter(0))
    time_diff = [math.fabs(time - time_path[0]) for time_path in time_filepath]
    min_index = time_diff.index(min(time_diff))
    return time_filepath[min_index][1]