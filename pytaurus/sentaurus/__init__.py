__author__ = 'Lunzhy'

Cell_Structure = 'triplefull'  # triple | triplefull

#paramter file name
User_Param_File = r'user.param'
TimeStep_File = 'timestep.in'

#the template filename in resource
Resource_Sse_File = r'%s_sse.template' % Cell_Structure
Resource_Sde_File = r'%s_sde.template' % Cell_Structure
Resource_Sde_File_Vth = r'triple_sde_vth.template' if Cell_Structure == 'triple' \
                        else r'%s_sde.template' % Cell_Structure
Resource_Ins_File = r'inspect.template'


#the folder to run sentaurus under project folder
Folder_Run_Sentaurus = r'sentrun'
Folder_Exchange_Data = r'exchange'

#the generated command name for sse dan sdevice
Sse_Cmd_File = r'sse_%s.cmd' % Cell_Structure
Sde_Cmd_File = r'sde_%s.cmd' % Cell_Structure
Inspect_Cmd_File = r'ins.cmd'

#names of file for data exchange
#from SimCTM
Points_Location_Subs = r'subs_points.in'
File_Interface_Vfb = r'charge.in'
#from Pytaurus
Subs_Data_File = r'substrate.in'
Plot_Subs_File = r'potential_fermi.out'

Tdr_File = r'%s_msh.tdr' % Cell_Structure
Plot_File = r'final_%s_des.plt' % Cell_Structure if Cell_Structure == 'triple' \
                                                    else r'extract_%s_des.plt' % Cell_Structure
Plot_File_Init = r'%s_des.plt' % Cell_Structure if Cell_Structure == 'triple' \
                                                    else r'init_%s_des.plt' % Cell_Structure


#the folder and file name for solving vth
Folder_Substrate = r'Substrate'
Charge_File_Prefix = r'VfbInterface'
Folder_Miscellaneous = r'Miscellaneous'
File_Vth = r'Vth.txt'
File_Parsed_Vth = r'Vth_flatband.txt'

#names of file for log
Logfile_Sse = r'sse_run.log'
Logfile_Sdevice = r'sde_run.log'

#physics constant
eps0 = 8.854187817e-14 # [F/cm]
q_charge = 1.602176487e-19 # [C]