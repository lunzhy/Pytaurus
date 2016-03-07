__author__ = 'Lunzhy'
import os, sys
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if path not in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen

Folder_Data_Band = 'Band'
Folder_Data_Current = 'Current'
Folder_Data_Density = 'Density'
Folder_Data_ElecField = 'ElecField'
Folder_Data_Potential = 'Potential'
Folder_Data_Substrate = sen.Folder_Substrate
Folder_Data_Trap = 'Trap'

Files_Remain = [sen.User_Param_File, sen.TimeStep_File, sen.Trapped_In_File, sen.Subs_Data_File]

Folers_In_Projects = [Folder_Data_Band, Folder_Data_Current, Folder_Data_Density, Folder_Data_ElecField,
                      Folder_Data_Potential, Folder_Data_Substrate, Folder_Data_Trap,
                      sen.Folder_Miscellaneous, sen.Folder_Run_Sentaurus, sen.Folder_Exchange_Data]
