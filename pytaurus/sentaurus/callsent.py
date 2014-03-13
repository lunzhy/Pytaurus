__author__ = 'lunzhy'
import os, sys, re, subprocess
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir)
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen

def callSse():
    return