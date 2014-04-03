__author__ = 'Lunzhy'

#paramter file name
User_Param_File = r'user.param'

#the template filename in resource
Resource_Sse_File = r'triple_sse.cmd'
Resource_Sde_File = r'triple_sde.cmd'
Resource_Ins_File = r'inspect.cmd'
Resource_Sde_File_Vth = r'triple_sde_vth.cmd'

#the folder to run sentaurus under project folder
Folder_Run_Sentaurus = r'sentrun'
Folder_Exchange_Data = r'exchange'

#the generated command name for sse dan sdevice
Sse_Cmd_File = r'sse_triple.cmd'
Sde_Cmd_File = r'sde_triple.cmd'
Inspect_Cmd_File = r'ins.cmd'

#names of file for data exchange
#from SimCTM
Points_Location_Subs = r'subs_points.in'
Charge_File = r'charge.in'
#from Pytaurus
Exchange_Data_Subs = r'substrate.in'
Tdr_File = r'triple_msh.tdr'
Plot_Subs_File = r'potential_fermi.out'
Plot_File_Sentaurus = r'final_triple_sde_des.plt'
Plot_File_Init_Sentaurus = r'triple_sde_des.plt'

#the folder and file name for solving vth
Folder_Substrate = r'Substrate'
Charge_File_Prefix = r'VfbInterface'
Folder_Miscellaneous = r'Miscellaneous'
File_Vth = r'Vth.txt'

#names of file for log
Logfile_Sse = r'sse_run.log'
Logfile_Sdevice = r'sde_run.log'

#physics constant
eps0 = 8.854187817e-14 # [F/cm]
q_charge = 1.602176487e-19 # [C]