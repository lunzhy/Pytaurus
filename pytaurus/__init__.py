__author__ = 'Lunzhy'
import os, sys
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen

Files_Remain = [sen.User_Param_File, sen.Subs_Data_File, sen.TimeStep_File]
